{
    'name': 'Kitchen Kraft Report Custom Font',
    'version': '1.4',
    'summary': 'Applies a custom font to all PDF reports',
    'description': """
        This module applies a custom dot matrix-style font globally across
        all QWeb PDF reports.
    """,
    'author': 'AGM Global Services',
    'category': 'Tools',
    'depends': ['web', 'base','account'],
    # 'data': [
    #     'views/report_templates.xml',
    # ],
    'assets': {
        'web.report_assets_common': [
            '/kitchenkraft_report_custom_font/static/src/scss/report_fonts.scss',
        ],
    },
    'installable': True,
    'application': False,
}
