# -*- coding: utf-8 -*-

import odoo
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.service import security

from odoo.addons.web.controllers.main import ensure_db

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

        threading.current_thread().uid = res

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

        return True

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

        blogs = blog_ids.read(['id', 'name'])
        for blog in blogs:
            data.append(
                {
                    'blogid': blog['id'],
                    'url': '%s/%s-%s' % ('/blog', blog['name'].lower(), blog['id']),
                    'blogName': blog['name']
                }
            )

        return data

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
                publish,
        }
        blog_post.write(vals)

        return True

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

        tag_ids = self.env['blog.tag'].search_read([], ['id', 'name'])
        blog_id = self.env['blog.blog'].search([('id', '=', int(blogid))])

        for tag in tag_ids:
            data.append(
                {
                    'categoryid': tag['id'],
                    'title': tag['name'],
                    'description': tag['name'],
                    'htmlurl': '/blog/%s-%s/tag/%s-%s' % (blog_id['name'], blog_id['id'], tag['name'], tag['id'])
                }
            )

        return data

    def exp_metaWeblog_getPost(self, postid, username, password):
        '''
        Return post
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

        '''

        if not self.check_permission(username, password):
            return
        blog_post = self.env['blog.post'].search([('id', '=', postid)])

        return {
            'dateCreated':
                blog_post.post_date and
                datetime.datetime.strftime(blog_post.post_date, DEFAULT_SERVER_DATETIME_FORMAT),
            'description':
                blog_post.content,
            'title':
                blog_post.name,
            'postid':
                blog_post['id'],
            'link':
                blog_post.website_url,
        }

    def exp_metaWeblog_getRecentPosts(self, blogid, username, password, numberOfPosts=20):
        '''
        Return post
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

        '''
        if not self.check_permission(username, password):
            return

        data = []
        blog_post_ids = self.env['blog.post'].search([('blog_id', '=', int(blogid))], limit=numberOfPosts)

        for blog_post in blog_post_ids:
            data.append(
                {
                    'dateCreated': datetime.datetime.strftime(blog_post.post_date, DEFAULT_SERVER_DATETIME_FORMAT),
                    'description': blog_post.content,
                    'title': blog_post.name,
                    'postid': blog_post['id']
                }
            )

        return data

    def exp_metaWeblog_newMediaObject(self, blogid, username, password, file):
        '''
        Params file
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
                'tag_ids': [(6, False, tag_ids.ids)],
                'post_date': datetime.datetime.strftime(datetime.datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT),
                'blog_id': blogid,
                'is_published': publish
            }
        )

        return postid.id

    def exp_wp_newCategory(self, blog_id, username, password, category):
        '''
        Params category
            name, string
            slug, string, optional
            parent_id, integer
            description, string, optional

        Return integer

        '''

        if not self.check_permission(username, password):
            return
        raise Exception("Not implemented...")


def dispatch(method, params):
    if not odoo.http.request.db:
        ensure_db()
        raise Exception("URL not found.")

    obj_metaweblog = MetaWeblog(odoo.http.request)

    if not obj_metaweblog.blog_installed():
        raise Exception("Website Blog is not installed.")

    exp_method_name = 'exp_' + method.replace('.', '_')
    if hasattr(obj_metaweblog, exp_method_name):
        return getattr(obj_metaweblog, exp_method_name)(*params)
    else:
        raise Exception("Method not found: %s" % method)
