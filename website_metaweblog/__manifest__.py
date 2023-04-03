# -*- coding: utf-8 -*-
{
    'name': "MetaWeblog API for blog",
    'summary': """
         """,
    'description': """
         
    """,
    'author': 'genin IT, jeffery <jeffery9@gmail.com>',
    'website': 'http://www.geninit.cn',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_blog'],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
    'post_load': 'post_load',
    'price': 50,
    'currency': 'EUR',
}
