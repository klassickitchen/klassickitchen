{
    'name': 'KitchenKraft Auto Intercompany Purchase',
    'version': '18.3.1',
    'category': 'Sales',
    'summary': 'Automatically create intercompany purchase orders',
    'depends': ['sale', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/intercompany_purchase_wizard_views.xml',
        'views/sale_order_views.xml'
    ],
    'installable': True,
    'application': True,
}