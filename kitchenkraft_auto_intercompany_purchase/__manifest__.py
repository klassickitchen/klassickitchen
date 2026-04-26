{
    "name": "KitchenKraft Auto Intercompany Purchase",
    "version": "18.6.8",
    "category": "Sales",
    "summary": "Automatically create intercompany purchase orders",
    "depends": ["sale", "purchase", "sale_purchase_inter_company_rules"],
    "data": [
        "security/ir.model.access.csv",
        "views/intercompany_purchase_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": True,
}
