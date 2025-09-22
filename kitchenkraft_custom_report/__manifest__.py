{
    'name': "Kitchenkraft Custom report",
    'version': '16.0.1',
    'summary': "Kitchenkraft Custom report",
    'description': "Kitchenkraft Custom report",
    'author': "AGM Info Solutions",
    'category': 'Base',
    'website': 'https://www.agmglobal.in/',
    'depends': ['sale','base'],
    'data': [
        'report/paper_format.xml',
        # 'report/sale_quotation_reports.xml',
        'report/kitchenkraft_template_dotmatrix.xml',
        'views/external_layout_dotmatrix.xml',
        'report/account_move_reports.xml',
        'report/account_move_template.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}