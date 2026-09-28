{
    'name': "User / Showroom Report Footer (Print PDF)",
    'version': '18.0.1.0.0',
    'summary': "Showroom-specific HTML footer for Print PDF Invoices based on selling user",
    'author': "AGM Global Services",
    'category': 'Accounting/Sales',
    'depends': [
        'base',
        'account',
        'sale',
        'point_of_sale',
        'invoice_sequence_custom',
    ],
    'data': [
        'views/res_users_views.xml',
        'reports/report_invoice_footer_template.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
