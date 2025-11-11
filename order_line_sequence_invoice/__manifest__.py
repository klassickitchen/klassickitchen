{
    'name': 'Invoice Line Sequence Number',
    'version': '18.0.1.0.0',
    'summary': 'Adds sequence numbers to invoice lines in form view and PDF report',
    'description': """This module adds automatic sequence numbers to the invoice lines """,
    'category': 'Accounting',
    'author': 'AGM Global Services',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_move_line_sequence_view.xml',
        'report/account_move_line_sequence_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}