{
    'name': 'Kitchen Kraft Quotation Custom',
    'version': '18.0.1.0',
    'description': 'Kitchen Kraft Quotation',
    'author': 'AGM Global Services',
    'website': 'http://agmglobal.co',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'views/sale_order_line.xml',
        'views/stock_move.xml',
        'reports/quotation_report.xml',
    ],
    'installable': True,
    'application': False,
}