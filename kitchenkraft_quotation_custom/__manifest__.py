{
    'name': 'Kitchen Kraft Quotation Custom',
    'version': '18.0.1.5',
    'description': 'Kitchen Kraft Quotation',
    'author': 'AGM Global Services',
    'website': 'http://agmglobal.co',
    # sale_stock owns stock.move.sale_line_id, used by product_sale_price.
    'depends': ['base', 'sale', 'stock', 'sale_stock', 'kitchenkraft_multiple_barcode'],
    'data': [
        'views/sale_order_line.xml',
        'views/stock_move.xml',
        'views/product_template_views.xml',
        'reports/quotation_report.xml',
    ],
    'installable': True,
    'application': False,
}
