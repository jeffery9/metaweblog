# -*- coding: utf-8 -*-

import odoo
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.service import security

from odoo.addons.web.controllers.main import ensure_db
from odoo.addons.http_routing.models.ir_http import slug

from xmlrpc.client import DateTime, Boolean

import base64
import datetime
import threading

import logging

_logger = logging.getLogger(__name__)
'''
need to implement those methods

1, blogger.deletePost
2, blogger.getUsersBlogs
3, metaWeblog.editPost
4, metaWeblog.getCategories
5, metaWeblog.getPost
6, metaWeblog.getRecentPosts
7, metaWeblog.newMediaObject
8, metaWeblog.newPost
9, wp.newCategory

'''


class MetaWeblog:
    def __init__(self, request):

        self.db = request.db
        self.base_url = request.httprequest.host_url
        # self.pool = odoo.registry(self.db)
        # self.pool.check_signaling()
        # self.cr = odoo.sql_db.db_connect(self.db).cursor()
        # self.cr.autocommit(True)

        # self.env = odoo.api.Environment(self.cr, odoo.SUPERUSER_ID, {})
        self.env = odoo.http.request.env

    def blog_installed(self):
        if not self.db:
            return False

        if 'blog.blog' in self.env:
            return True

        return False

    def check_permission(self, username, password):
        res = security.login(self.db, username, password)
        msg = res and 'successful login' or 'bad login or password'
        _logger.info("%s from '%s' using database '%s'", msg, username, self.db.lower())
        if not res:
            return False

        # threading.current_thread().uid = res

        user_id = self.env['res.users'].search([('id', '=', res)], limit=1)
        if user_id and user_id.has_group('website.group_website_designer'):
            self.env.uid = user_id.id
            return True

        return False

    def exp_blogger_deletePost(self, appKey, postid, username, password, publish=True):
        '''

        Return true, Always returns true.

        '''
        if not self.check_permission(username, password):
            return

        self.env['blog.post'].search([('id', '=', int(postid))]).unlink()

        return Boolean(True)

    def exp_metaWeblog_deletePost(self, appKey, postid, username, password, publish=True):
        return self.exp_blogger_deletePost(appKey, postid, username, password, publish)

    def exp_blogger_getUsersBlogs(self, appKey, username, password):
        '''
        Return list of BlogInfo
            blogid
            url
            blogName
        '''
        if not self.check_permission(username, password):
            return

        blog_ids = self.env['blog.blog'].search([])

        data = []
        for blog_id in blog_ids:
            data.append(
                {
                    'blogid': str(blog_id['id']),
                    'url': '%s/blog/%s' % (self.base_url.strip('/'), slug(blog_id)),
                    'blogName': blog_id['name']
                }
            )

        return data

    def exp_metaWeblog_getUsersBlogs(self, appKey, username, password):
        return self.exp_blogger_getUsersBlogs(appKey, username, password)

    def exp_metaWeblog_editPost(self, postid, username, password, post, publish=True):
        '''
        Return  any
        '''

        if not self.check_permission(username, password):
            return

        blog_post = self.env['blog.post'].search([('id', '=', postid)])
        tag_ids = self.env['blog.tag'].search([('name', 'in', post['categories'])])
        vals = {
            'name':
                post['title'],
            'content':
                post['description'],
            'tag_ids':
                tag_ids.ids and [(6, False, tag_ids.ids)] or [(5, False, False)],
            'post_date':
                'dateCreated' in post and datetime.datetime.strftime(
                    datetime.datetime.strptime(post['dateCreated'].value, "%Y%m%dT%H:%M:%S"),
                    DEFAULT_SERVER_DATETIME_FORMAT
                ) or datetime.datetime.strftime(datetime.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
            'is_published':
                Boolean(publish)
        }
        blog_post.write(vals)

        return Boolean(True)

    def exp_metaWeblog_getCategories(self, blogid, username, password):
        '''
        Return  CategoryInfo
            description, string
            htmlurl, string
            rssurl, string
            title, string
            categoryid, string
        '''

        if not self.check_permission(username, password):
            return

        data = []

        tag_ids = self.env['blog.tag'].search([])
        blog_id = self.env['blog.blog'].search([('id', '=', int(blogid))])

        for tag in tag_ids:
            data.append(
                {
                    'categoryid': str(tag['id']),
                    'title': tag['name'],
                    'description': tag['name'],
                    'htmlUrl': '%s/blog/%s/tag/%s' % (self.base_url.strip('/'), slug(blog_id), slug(tag)),
                    'rssUrl': ''
                }
            )

        return data

    def exp_metaWeblog_getPost(self, postid, username, password):
        '''
        Params 
            postid, string

        Return post struct
            dateCreated, dateTime.iso8601
            description, string
            title, string
            enclosure struct
                length, int4
                type, string, optional
                url, string, optional
            categories, list of string, optional
            link, optional
            permalink, optional
            postid, string, optional
            userid, string, optional
            source
                name, string, optional
                url, string, optional

        '''

        if not self.check_permission(username, password):
            return
        blog_post = self.env['blog.post'].search([('id', '=', int(postid))])

        post = {
            'dateCreated': blog_post.post_date and DateTime(blog_post.post_date),
            'description': blog_post.content,
            'title': blog_post.name,
            'enclosure': {
                'length': 0,
            },
            'link': '%s%s' % (self.base_url.strip('/'), blog_post.website_url),
            'permalink': '%s%s' % (self.base_url.strip('/'), blog_post.website_url),
            'postid': blog_post.id,
            'userid': str(self.env.uid),
            'source': {},
            'mt_keywords': ''
        }
        if blog_post.tag_ids:
            post.update({'categories': blog_post.tag_ids.mapped('name')})

        return post

    def exp_metaWeblog_getRecentPosts(self, blogid, username, password, numberOfPosts=20):
        '''
        Params 
            blogid, string

        Return list of post struct
            dateCreated, dateTime.iso8601
            description, string
            title, string
            enclosure struct
                length, int4
                type, string, optional
                url, string, optional
            categories, list of string, optional
            link, optional
            permalink, optional
            postid, string, optional
            userid, string, optional
            source
                name, string, optional
                url, string, optional

        '''
        if not self.check_permission(username, password):
            return

        data = []
        blog_post_ids = self.env['blog.post'].search([('blog_id', '=', int(blogid))], limit=numberOfPosts)

        for blog_post in blog_post_ids:
            post = {
                'dateCreated': blog_post.post_date and DateTime(blog_post.post_date),
                'description': blog_post.content,
                'title': blog_post.name,
                'enclosure': {
                    'length': 0
                },
                'link': '%s%s' % (self.base_url.strip('/'), blog_post.website_url),
                'permalink': '%s%s' % (self.base_url.strip('/'), blog_post.website_url),
                'postid': str(blog_post['id']),
                'source': {},
                'userid': str(self.env.uid)
            }

            if blog_post.tag_ids:
                post.update({
                    'categories': blog_post.tag_ids.mapped('name'),
                })

            data.append(post)

        return data

    def exp_metaWeblog_newMediaObject(self, blogid, username, password, file):
        '''
        Params 
            file struct
                bits, base64
                name, string
                type, string

        Return urldata
            url, string

        '''
        if not self.check_permission(username, password):
            return

        image_types = ['image/gif', 'image/jpe', 'image/jpeg', 'image/jpg', 'image/gif', 'image/png', 'image/svg+xml']

        bin_data = base64.standard_b64encode(file['bits'].data)
        name = file['name']
        if name:
            media_name = name.split('/').pop()
        bin_type = file['type']

        if bin_type not in image_types:
            raise Exception('Not support media type: %s' % bin_type)

        res_model = 'ir.ui.view'
        res_id = False

        attachment_data = {
            'name': media_name,
            'public': True,
            'res_id': res_id,
            'res_model': res_model,
            'datas': bin_data
        }

        attachment_id = self.env['ir.attachment'].create(attachment_data)

        media_info = attachment_id._get_media_info()
        return {'url': media_info['image_src']}

    def exp_metaWeblog_newPost(self, blogid, username, password, post, publish=True):
        '''
        Params post
            dateCreated
            description
            title
            categories, list of string, optional
            enclosure, optional
                length, integer, optiona
                type, string, optional
                url, string, optional
            link, optional
            permalink, optional
            postid, optional
            source, optional
                name, string, optional
                url, string, optional

        Return postid as string

        '''

        if not self.check_permission(username, password):
            return

        tag_ids = self.env['blog.tag'].search([('name', 'in', post['categories'])])
        postid = self.env['blog.post'].create(
            {
                'name': post['title'],
                'content': post['description'],
                'tag_ids': tag_ids.ids and [(6, False, tag_ids.ids)] or [(5, False, False)],
                'post_date': datetime.datetime.strftime(datetime.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
                'blog_id': int(blogid),
                'is_published': Boolean(publish)
            }
        )

        return str(postid.id)

    def exp_wp_newCategory(self, blog_id, username, password, category):
        '''
        Params category struct
            name, string
            slug, string, optional
            parent_id, integer
            description, string, optional

        Return integer

        '''

        if not self.check_permission(username, password):
            return

        tag_val = {
            'name': category['name'],
        }
        tag_id = self.env['blog.tag'].create(tag_val)
        return tag_id.id


def dispatch(method, params):
    if not odoo.http.request.db:
        ensure_db()
        raise Exception("URL not found.")

    obj_metaweblog = MetaWeblog(odoo.http.request)

    if not obj_metaweblog.blog_installed():
        raise Exception("Website Blog is not installed.")

    exp_method_name = 'exp_' + method.replace('.', '_')
    if hasattr(obj_metaweblog, exp_method_name):
        _logger.info("Method '%s' called. " % method)
        return getattr(obj_metaweblog, exp_method_name)(*params)
    else:
        raise Exception("Method not found: %s" % method)
