{
    'name': 'Kitchenkraft Stock Restrict',
    'version': '1.0',
    'summary': 'Restrict sale of out-of-stock products based on product configuration',
    'author': 'AGM Global Services',
    'license': 'OPL-1',
    'depends': ['sale_management', 'stock', 'product', 'point_of_sale'],
    'data': [
        'views/product_variant_views.xml',
    ],
    'assets': {
            'point_of_sale._assets_pos': [
                'kitchenkraft_stock_restrict/static/src/js/ProductScreen.js',
                'kitchenkraft_stock_restrict/static/src/css/display_stock.css',
                'kitchenkraft_stock_restrict/static/src/xml/ProductItem.xml',
            ],
        },
    'installable': True,
    'application': False,
}
