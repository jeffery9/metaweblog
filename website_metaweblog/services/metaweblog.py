# -*- coding: utf-8 -*-

import odoo

import datetime

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

db = odoo.http.request.db
registry = odoo.registry(db)

env = odoo.api.Environment(registry.cursor(), odoo.SUPERUSER_ID, {})

if db:
    user_model = env['res.users']

    blog_model = env['blog.blog']
    blog_tag_category_model = env['blog.tag.category']
    blog_tag_model = env['blog.tag']
    blog_post_model = env['blog.post']


def blog_installed():
    if not db:
        return False

    if 'blog.blog' in env:
        return True

    return False


def check_permission(username, password):
    uid = user_model.authenticate(db, username, password, None)
    if uid and user_model.browse(uid).has_group('website.group_website_designer'):
        return True
    return False


def exp_blogger_deletePost(appKey, postid, username, password, publish=True):
    '''

    Return true, Always returns true.

    '''
    if not check_permission(username, password):
        return
    raise Exception("Not implemented...")


def exp_blogger_getUsersBlogs(appKey, username, password):
    '''
    Return list of BlogInfo
        blogid
        url
        blogName
    '''
    if not check_permission(username, password):
        return

    blog_ids = blog_model.search([])

    data = []

    blogs = blog_ids.read(['id', 'name'])
    for blog in blogs:
        data.append(
            {
                'blogid': blog['id'],
                'url': '%s/%s-%s' % ('/blog', blog['name'], blog['id']),
                'blogName': blog['name']
            }
        )

    return data


def exp_metaWeblog_editPost(postid, username, password, post, publish=True):
    '''
    Return  any
    '''

    if not check_permission(username, password):
        return

    blog_post = blog_post_model.search([('id', '=', postid)])

    blog_post.write({
        'dateCreated': blog_post.post_date,
        'description': blog_post.content,
        'title': blog_post.name,
    })

    return True


def exp_metaWeblog_getCategories(blogid, username, password):
    '''
    Return  CategoryInfo
        description, string
        htmlurl, string
        rssurl, string
        title, string
        categoryid, string
    '''

    if not check_permission(username, password):
        return

    data = []

    tag_ids = blog_tag_model.search_read([], ['id', 'name'])
    blog_id = blog_model.search([('id', '=', int(blogid))])

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


def exp_metaWeblog_getPost(postid, username, password):
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

    if not check_permission(username, password):
        return
    blog_post = blog_post_model.search([('id', '=', postid)])

    return {
        'dateCreated': blog_post.post_date,
        'description': blog_post.content,
        'title': blog_post.name,
        'postid': blog_post['id']
    }


def exp_metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts=20):
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
    if not check_permission(username, password):
        return

    data = []
    blog_post_ids = blog_post_model.search([('blog_id', '=', int(blogid))], limit=numberOfPosts)

    for blog_post in blog_post_ids:
        data.append(
            {
                'dateCreated': blog_post.post_date,
                'description': blog_post.content,
                'title': blog_post.name,
                'postid': blog_post['id']
            }
        )

    return data


def exp_metaWeblog_newMediaObject(blogid, username, password, file):
    '''
    Params file
        bits, base64
        name, string
        type, string

    Return urldata
        url, string

    '''
    if not check_permission(username, password):
        return
    raise Exception("Not implemented...")


def exp_metaWeblog_newPost(blogid, username, password, post, publish=True):
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

    if not check_permission(username, password):
        return

    tag_ids = blog_tag_model.search([('name', 'in', post['categories'])])
    postid = blog_post_model.create(
        {
            'name': post['title'],
            'content': post['description'],
            'tag_ids': [(6, False, tag_ids.ids)],
            'post_date': datetime.datetime.now(),
            'blog_id': blogid
        }
    )
    return postid.id


def exp_wp_newCategory(blog_id, username, password, category):
    '''
    Params category
        name, string
        slug, string, optional
        parent_id, integer
        description, string, optional

    Return integer

    '''

    if not check_permission(username, password):
        return
    raise Exception("Not implemented...")


def dispatch(method, params):
    if not blog_installed():
        raise Exception("Website Blog is not installed.")

    g = globals()
    exp_method_name = 'exp_' + method.replace('.', '_')
    if exp_method_name in g:
        return g[exp_method_name](*params)
    else:
        raise Exception("Method not found: %s" % method)
