# -*- coding: utf-8 -*-
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


class BlogInfo():
    def __init__(self, blogid, url, blogName):
        self.blogid = blogid
        self.url = url
        self.blogName = blogName


def exp_blogger_deletePost(appKey, postid, username, password, publish):
    raise Exception("Not implemented...")


def exp_blogger_getUsersBlogs(appKey, username, password):
    raise Exception("Not implemented...")


def exp_metaWeblog_editPost(postid, username, password, post, publish):
    raise Exception("Not implemented...")


def exp_metaWeblog_getCategories(blogid, username, password):
    raise Exception("Not implemented...")


def exp_metaWeblog_getPost(blogid, username, password):
    raise Exception("Not implemented...")


def exp_metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts):
    raise Exception("Not implemented...")


def exp_metaWeblog_newMediaObject(blogid, username, password, file):
    raise Exception("Not implemented...")


def exp_metaWeblog_newPost(blogid, username, password, post, publish):
    raise Exception("Not implemented...")


def exp_wp_newCategory(blog_id, username, password, category):
    raise Exception("Not implemented...")


def dispatch(method, params):

    g = globals()
    exp_method_name = 'exp_' + method.replace('.', '_')
    if exp_method_name in g:
        return g[exp_method_name](*params)
    else:
        raise Exception("Method not found: %s" % method)
