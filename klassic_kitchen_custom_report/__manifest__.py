{
    'name': "klassic_kitchen_custom_report",
    'version': '16.0.1',
    'summary': "klassic_kitchen_custom_report",
    'description': "klassic_kitchen_custom_report",
    'author': "AGM Info Solutions",
    'category': 'Base',
    'website': 'https://www.agmglobal.in/',
    'depends': ['sale','base'],
    'data': [
        'report/paper_format.xml',
        # 'report/sale_quotation_reports.xml',
        'report/klassic_kitchen_template_dotmatrix.xml',
        'views/external_layout_dotmatrix.xml',
        'report/account_move_reports.xml',
        'report/account_move_template.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}