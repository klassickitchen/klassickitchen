{
    'name': "Header and Footer for KitchenKraft",
    'version': '18.1.2',
    'author': 'AGM Global Services',
    'description': """Header and Footer for KitchenKraft""",
    'depends': ['sale_management', 'sale', 'stock', 'web', 'base', 'account'],
    'data': [
        'reports/report_template.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',

}