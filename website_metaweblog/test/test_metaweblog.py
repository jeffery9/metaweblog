import xmlrpc.client

url = 'http://127.0.0.1:8069'

# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# version = common.version()
# print(version)

method_lists = [
    'blogger.deletePost',
    'blogger.getUsersBlogs',
    'metaWeblog.editPost',
    'metaWeblog.getCategories',
    'metaWeblog.getPost',
    'metaWeblog.getRecentPosts',
    'metaWeblog.newMediaObject',
    'metaWeblog.newPost',
    'wp.newCategory']

metaweblog = xmlrpc.client.ServerProxy('{}/xmlrpc/2/metaweblog'.format(url))

print(metaweblog)

for method in method_lists:
    print(method)
    fn = eval('%s.%s' % ('metaweblog', method))
    print(fn)
    result = fn()
    print(result)
