{
    "name": "POS Fixed Discount",
    "version": "18.0.0.1.0",
    "category": "Point of Sale",
    "summary": "Apply fixed amount discounts on Point of Sale orders",
    "description": """
This module allows POS users to apply a fixed discount amount
directly on POS order lines or orders, enhancing pricing flexibility
during sales operations.
    """,
    "author": "AGM Info Solutions",
    "website": "https://www.agmglobal.in/",
    "depends": ["pos_discount"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_fixed_discount/static/src/js/fixed_discount_button.js",
            "pos_fixed_discount/static/src/xml/fixed_discount_button.xml",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
