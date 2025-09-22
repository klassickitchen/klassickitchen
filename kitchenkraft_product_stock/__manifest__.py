{
    'name': 'KitchenKraft Product Stock',
    'version': '18.1.0',
    'summary': 'Adds a Stock Details button to sale order lines',
    'description': 'This module adds a custom button to sale order lines to view stock details.',
    'author': 'AGM Global Services',
    'website': 'https://www.agmglobal.co/',
    'category': 'Sales',
    'depends': ['sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/stock_details_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
}