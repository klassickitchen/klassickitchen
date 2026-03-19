{
	'name': "Custom invoice sequence number",
	'version': '18.0.3.10.4',
	'category': 'Point of Sale',
	'summary': "This module is used to add custom serial number for invoices",
    'author': 'AGM Global Services',
    'website': 'http://agmglobal.co',
    'depends': ['base','point_of_sale','account','res_company_code', 'stock_picking_invoice_link', 'amount_in_words_invoice', 'order_line_sequence_invoice'],
	'data': [
        'report/custom_report_a5.xml',
        'report/report_invoice_a5.xml',
        'report/report_pos_invoice.xml',
        # 'data/pos_invoice_sequence.xml',
		'views/account_move_views.xml',
		'views/sale_order_views.xml',
	],
	'assets': {
				'point_of_sale._assets_pos': [
					'invoice_sequence_custom/static/src/js/payment_screeen.js',
				],
			},
	'license': 'AGPL-3',
	'installable': True,
	'auto_install': False,
	'application': False,
}
