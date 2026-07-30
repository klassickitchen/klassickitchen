# -*- coding: utf-8 -*-
{
    "name": "POS Global Discount Auto Calculation",
    "version": "18.0.2.0.0",
    "author": "AGM Info Solutions",
    "website": "https://www.agmglobal.in/",
    "category": "Point Of Sale",
    "summary": "Auto calculate equivalent Fixed/Percentage discount in POS Global Discount popup, "
               "and keep the invoiced total in agreement with the amount collected",
    "description": """
        When the user enters a Fixed Discount value, the system automatically calculates
        and displays the equivalent Percentage Discount, and vice versa.

        Also fixes two defects that left POS invoices permanently "Partially Paid".
        Full analysis: documents/klassic_kitchen/POS_ROUNDING_ISSUE.md

        1. Fractional discount percentages (primary)
           A fixed-amount global discount back-calculates its percentage by
           division, which rarely lands on two decimals -- 3264 / 13054 * 100 =
           25.003830243603492. pos.order.line.discount is declared digits=0 so
           POS stored all of it, while account.move.line.discount is limited to
           the 'Discount' precision, so the invoice silently re-priced every
           line at a different discount than the till used. The percentage is
           now quantised in POS, and the popup previews the quantised result so
           the cashier sees the total that will actually be charged.

        2. Refunds landing on an exact rounding tie
           POS inverts the cash-rounding tie-break when the amount due is
           negative (getRoundedRemaining in pos_order.js); account.move does
           not, so a 3.50 refund was paid out as 3.00 but invoiced as 4.00.
           Refund invoices now use a mirrored account.cash.rounding.

        Also mirrors POS's shouldRound() on the invoice, so enabling
        "Only round cash method" no longer rounds card and bank-transfer
        invoices that the till left unrounded.

        No data migration. Invoices already posted keep the values they were
        posted with.
    """,
    "depends": ["sh_pos_order_discount", "account"],
    "application": False,
    "assets": {
        "point_of_sale._assets_pos": [
            "sh_pos_show_discount/static/src/**/*",
        ],
    },
    "auto_install": False,
    "installable": True,
}
