{
    'name': 'kitchenkraft Multiple Barcode',
    'version': '18.2.1',
    'category': 'Inventory',
    'summary': 'Multiple Barcode for kitchenkraft',
    'depends': ['product', 'point_of_sale', 'stock','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/multiple_barcode_views.xml',
        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': True,
}