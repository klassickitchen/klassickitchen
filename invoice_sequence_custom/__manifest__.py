{
	'name': "Custom invoice sequence number",
	'version': '18.0.2.0.1',
	'category': 'Point of Sale',
	'summary': "This module is used to add custom serial number for invoices",
    'author': 'AGM Global Services',
    'website': 'http://agmglobal.co',
    'depends': ['base','point_of_sale','account','res_company_code'],
	'data': [
        'report/report_invoice_a5.xml',
        'report/report_pos_invoice.xml',
        'data/pos_invoice_sequence.xml',
		'views/account_move_views.xml',
	],

	'license': 'AGPL-3',
	'installable': True,
	'auto_install': False,
	'application': False,
}
