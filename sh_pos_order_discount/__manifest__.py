# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Point Of Sale Order Discount",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "license": "OPL-1",
    "summary": """POS Order Discount Sales Discount Management Discount Application in POS In-Store Order Discounts Flexible Discount Options Discount Codes for POS POS Discount Promotions Real-time Discount Calculation Automatic Discounting in POS Customizable Discount Rules Discount per Order in POS Discounting at Checkout Dynamic Order Discounting Discount on Point of Sale Orders Discount Authorization in POS Product Discount Point Of Sale Discount Point Of Sale Order Line Discount POS Custom Discount Point Of Sale Global Discount Point Of Sale Line Discount POS Line Discount POS Global Discount POS Order Discount POS Order Line Discount Odoo Discount POS Discount in POS Discount In Point of Sales Trade Discounts Fixed Discounts Cash Discounts Threshold Discounts Percentage Discounts Set Discounts Manage Discounts Offer Discounts POS Discounts Discount On Sale Orders Discount On Sales Orders Discount On POS Orders Discount On Point Of Sale Orders """,
    "description": """Currently, in odoo point of sale, you can apply discount individually on every order line only. The "Point Of Sale Order Discount" module allows you to give discounts globally. This module applies the discounts on the point of sale order line as well as on the whole order. You can apply multiple discounts per order & order line. The discount can be applied in a fixed amount or percentage amount. Applied discount print on the receipt.""",
    "version": "0.0.3",
    "depends": ["point_of_sale"],
    "application": True,
    "data": ["views/res_config_settings_views.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "web/static/lib/jquery/jquery.js",
            "sh_pos_order_discount/static/src/**/*",
        ],
    },
    "auto_install": False,
    "installable": True,
    "images": [
        "static/description/background.png",
    ],
    "price": 20,
    "currency": "EUR",
}
