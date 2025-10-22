{
    'name': 'KitchenKraft Analytic Account',
    'version': '18.1.0',
    'summary': 'Link sale order to analytic account',
    'description': 'This module Link sale order to analytic account.',
    'author': 'AGM Global Services',
    'website': 'https://www.agmglobal.co/',
    'category': 'Sales',
    'depends': ['base','sale','account','purchase','crm'],
    'data': [
        # 'views/sales_team_views.xml',
        'views/res_user_preferences_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}