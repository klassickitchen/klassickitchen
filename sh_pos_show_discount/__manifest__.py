# -*- coding: utf-8 -*-
{
    "name": "POS Global Discount Auto Calculation",
    "version": "18.0.1.0.3",
    "author": "AGM Info Solutions",
    "website": "https://www.agmglobal.in/",
    "category": "Point Of Sale",
    "summary": "Auto calculate equivalent Fixed/Percentage discount in POS Global Discount popup",
    "description": """
        When the user enters a Fixed Discount value, the system automatically calculates
        and displays the equivalent Percentage Discount, and vice versa.
    """,
    "depends": ["sh_pos_order_discount"],
    "application": False,
    "assets": {
        "point_of_sale._assets_pos": [
            "sh_pos_show_discount/static/src/**/*",
        ],
    },
    "auto_install": False,
    "installable": True,
}
