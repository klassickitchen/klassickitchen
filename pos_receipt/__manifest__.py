{
    'name': 'Custom POS Receipt',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Customize POS receipt layout',
    'depends': ['point_of_sale'],
    'assets': {

        'point_of_sale._assets_pos': [
            'pos_receipt/static/src/js/PosOrder.js',
            'pos_receipt/static/src/js/CustomOrderReceipt.js',
            'pos_receipt/static/src/js/ReprintReceiptScreen.js',
            'pos_receipt/static/src/css/receipt.css',
            'pos_receipt/static/src/xml/OrderReceipt.xml',
            'pos_receipt/static/src/xml/ReceiptContact.xml',
        ],
    },
    'installable': True,
    'application': False,
}