# -*- coding: utf-8 -*-
{
    "name": "POS Global Discount Auto Calculation",
    "version": "18.0.2.0.1",
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

        2. "Only round cash method" was ignored on the invoice
           Core sets invoice_cash_rounding_id unconditionally while POS honours
           the flag, so enabling it would round card and bank-transfer invoices
           that the till left unrounded. _should_round_invoice() now mirrors
           POS's shouldRound().

        NOT a defect: refunds landing on an exact .50 tie. An earlier build
        mirrored the cash-rounding tie-break for refunds; that was reverted in
        18.0.2.0.1 after measuring 106 such refunds -- 101 already agreed with
        the invoice and only 5 did not. See the comment in models/pos_order.py
        before considering it again.

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
