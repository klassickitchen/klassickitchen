# -*- coding: utf-8 -*-
{
    "name": "Kitchenkraft POS Direct Print",
    "summary": "Direct printing of POS receipts and A4 tax invoices without browser dialogs",
    "category": "Point of Sale",
    "version": "18.0.1.0.5",
    "sequence": 1,
    "author": "Kitchen Kraft / Klassic Kitchen",
    "license": "Other proprietary",
    "depends": ["point_of_sale", "wk_odoo_direct_print"],
    "data": [
        "views/pos_config_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "kitchenkraft_pos_direct_print/static/src/app/direct_printer.js",
            "kitchenkraft_pos_direct_print/static/src/overrides/main.js",
            "kitchenkraft_pos_direct_print/static/src/overrides/navbar.xml",
            "kitchenkraft_pos_direct_print/static/src/overrides/order_receipt.xml",
            "kitchenkraft_pos_direct_print/static/src/overrides/pos_store.js",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
