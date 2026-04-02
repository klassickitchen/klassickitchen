{
    "name": "kitchenkraft Multiple Barcode",
    "version": "18.12.8",
    "category": "Inventory",
    "summary": "Multiple Barcode for kitchenkraft",
    "license": "OPL-1",
    "depends": [
        "product",
        "point_of_sale",
        "stock",
        "web",
        "stock_barcode",
    ],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/multiple_barcode_views.xml",
        "views/product_template_view.xml",
        "views/product_price_views.xml",
        "report/product_label_report.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "kitchenkraft_multiple_barcode/static/src/js/pos_order_line_patch.js",
            "kitchenkraft_multiple_barcode/static/src/js/product_screen.js",
            "kitchenkraft_multiple_barcode/static/src/js/product_screen_extension.js",
            "kitchenkraft_multiple_barcode/static/src/js/pos_barcode_search.js"
        ],
    },
    "installable": True,
    "application": True,
}
