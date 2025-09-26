{
    "name": "kitchenkraft Multiple Barcode",
    "version": "18.2.1",
    "category": "Inventory",
    "summary": "Multiple Barcode for kitchenkraft",
    "license": "OPL-1",
    "depends": [
        "product",
        "point_of_sale",
        "stock",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/multiple_barcode_views.xml",
        "views/product_template_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "kitchenkraft_multiple_barcode/static/src/js/pos_order_line_patch.js",
            "kitchenkraft_multiple_barcode/static/src/js/product_screen.js",
        ],
    },
    "installable": True,
    "application": True,
}
