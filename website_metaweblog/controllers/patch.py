# -*- coding: utf-8 -*-

import logging
import os
import sys
import threading
import time

try:
    import psutil
except ImportError:
    psutil = None

from odoo import http, netsvc, addons, exceptions, tools
from odoo.service.server import memory_info

_logger = logging.getLogger(__name__)
rpc_request = logging.getLogger(__name__ + '.rpc.request')
rpc_response = logging.getLogger(__name__ + '.rpc.response')


def patch_dispatch_rpc():
    _logger.info('Patching Dispatch RPC http.dispatch_rpc')

    dispatch_rpc = http.dispatch_rpc

    def new_dispatch_rpc(service_name, method, params):
        try:
            rpc_request_flag = rpc_request.isEnabledFor(logging.DEBUG)
            rpc_response_flag = rpc_response.isEnabledFor(logging.DEBUG)
            if rpc_request_flag or rpc_response_flag:
                start_time = time.time()
                start_memory = 0
                if psutil:
                    start_memory = memory_info(psutil.Process(os.getpid()))
                if rpc_request and rpc_response_flag:
                    netsvc.log(rpc_request, logging.DEBUG, '%s.%s' % (service_name, method),
                               http.replace_request_password(params))

            threading.current_thread().uid = None
            threading.current_thread().dbname = None

            if service_name == 'metaweblog':
                dispatch = addons.website_metaweblog.services.metaweblog.dispatch

                result = dispatch(method, params)

                if rpc_request_flag or rpc_response_flag:
                    end_time = time.time()
                    end_memory = 0
                    if psutil:
                        end_memory = memory_info(psutil.Process(os.getpid()))
                    logline = '%s.%s time:%.3fs mem: %sk -> %sk (diff: %sk)' % (
                        service_name, method, end_time - start_time, start_memory / 1024, end_memory / 1024,
                        (end_memory - start_memory) / 1024)
                    if rpc_response_flag:
                        netsvc.log(rpc_response, logging.DEBUG, logline, result)
                    else:
                        netsvc.log(rpc_request, logging.DEBUG, logline, http.replace_request_password(params), depth=1)

                return result

            else:
                return dispatch_rpc(service_name, method, params)

        except http.NO_POSTMORTEM:
            raise
        except exceptions.DeferredException as e:
            _logger.exception(tools.exception_to_unicode(e))
            tools.debugger.post_mortem(tools.config, e.traceback)
            raise
        except Exception as e:
            _logger.exception(tools.exception_to_unicode(e))
            tools.debugger.post_mortem(tools.config, sys.exc_info())
            raise

    addons.base.controllers.rpc.dispatch_rpc = new_dispatch_rpc


def post_load():
    patch_dispatch_rpc()
