{
    "name": "POS Ticket Screen Custom",
    "version": "18.0.0.0.1",
    "category": "Point of Sale",
    "summary": "Customizes POS Ticket Screen with Invoice and Mobile search",
    "author": "AGM Global Services",
    "website": "http://agmglobal.co",
    "depends": ["base", "point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_ticket_screen_custom/static/src/overrides/components/ticket_screen/ticket_screen.xml",
            "pos_ticket_screen_custom/static/src/overrides/components/ticket_screen/ticket_screen.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
