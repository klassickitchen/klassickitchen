{
	'name': "Restrict POS Global Discount",
	'version': '18.0.1.0.0',
	'category': 'Point of Sale',
	'summary': "This module is used to limit the POS Global discount ",
    'author': 'AGM Global Services',
    'website': 'http://agmglobal.co',
    'depends': ['point_of_sale','pos_discount'],
	'data': [
		'views/pos_config_views.xml',
	],
	'assets': {
        'point_of_sale._assets_pos': [
            'discount_limit/static/src/js/discount_limit.js',
        ],
    },
	'license': 'AGPL-3',
	'installable': True,
	'auto_install': False,
	'application': False,
}
