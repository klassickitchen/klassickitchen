{
    'name': "Header and Footer for KitchenKraft",
    'version': '18.1.9',
    'author': 'AGM Global Services',
    'description': """Header and Footer for KitchenKraft""",
    'depends': ['sale_management', 'sale', 'stock', 'web', 'base', 'account'],
    'data': [
        'reports/report_template.xml',
        'views/res_company_views.xml',
        # 'views/ir_action_report.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/kitchenkraft_header_and_footer/static/src/scss/style.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',

}