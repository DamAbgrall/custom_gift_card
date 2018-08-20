# -*- coding: utf-8 -*-
{
    'name': "Custom gift card",

    'summary': """Allow you to sell and use gift cards in the POS module""",

    'description': """This modules allows you to sell or create gift cards for your contacts and use them as a payment method in the POS module """,

	'author': "Noosys",
    'website': "http://btbc.fr/",

    'category': 'Point Of Sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','point_of_sale'],

    # always loaded
    'data': [
        'views/point_of_sale.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
	'js': ['static/src/js/config.js'],
	'qweb': ['static/src/xml/pos.xml']
}