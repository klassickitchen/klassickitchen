# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Why there is no refund tie-break mirroring here
# ---------------------------------------------------------------------------
# An earlier version of this file pointed refund invoices at a mirrored
# account.cash.rounding using the opposite tie-break (HALF-UP -> HALF-DOWN), on
# the theory that POS inverts the tie-break for refunds while account.move does
# not. That was wrong, and it was reverted after measuring the real data.
#
# getRoundedRemaining() in point_of_sale/static/src/app/models/pos_order.js does
# contain an inversion, but it only fires when `remaining` is negative -- and for
# a refund `remaining` is NOT negative. taxTotals is built with
# `quantity: documentSign * line.qty` (pos_order.js:131-141), so every base line
# of a refund is made positive and `order_remaining` is a positive magnitude. The
# sign is re-applied afterwards in getDefaultAmountDueToPayIn as
# `order_sign * amount`. The inversion therefore applies to change/overpayment on
# a normal sale, never to refunds.
#
# Measured on klassic300726 over 106 refunds landing on an exact .50 tie:
#
#     POS paid AWAY from zero (-389.00 for -388.50)  101 orders
#     POS paid TOWARD zero    (-304.00 for -304.50)    5 orders
#
# account.move applies HALF-UP to the positive refund total, giving 389.00 -- so
# it already agrees with POS in 101 of 106 cases. Mirroring the tie-break would
# have inverted the invoice for all 101 and broken them, to "fix" 5.
#
# The 5 outliers are all Cash, all on config 2, spread over four months. Their
# payment amount is the floor of the total, which is what a cashier gets by
# overwriting the prefilled amount -- check_cash_rounding_has_been_well_applied()
# accepts any whole riyal, so 304 passes validation just as 305 does. They are a
# data/procedure difference, not a code defect: the till handed over one riyal
# less than the credit note says. Treat them as write-offs, not as a bug.
#
# Do not re-add the mirroring without re-measuring that distribution first.
# ---------------------------------------------------------------------------


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _should_round_invoice(self):
        """Mirror of shouldRound() in pos_order.js.

        _prepare_invoice_vals() in core sets invoice_cash_rounding_id
        unconditionally, while POS only rounds when this returns true. With
        "Only round cash method" enabled the invoice would round card and
        bank-transfer orders that the till left unrounded, producing a
        collected-vs-invoiced mismatch on every non-cash order.

        The flag is off on both configs today, so this changes nothing now --
        it removes a trap for whoever ticks it later.
        """
        self.ensure_one()
        config = self.config_id
        if not (config.cash_rounding and config.rounding_method):
            return False
        if not config.only_round_cash_method:
            return True
        return any(p.payment_method_id.is_cash_count for p in self.payment_ids)

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if not self._should_round_invoice() and vals.get("invoice_cash_rounding_id"):
            _logger.debug(
                "POS %s: clearing invoice cash rounding, POS did not round this order.",
                self.name,
            )
            vals["invoice_cash_rounding_id"] = False
        return vals
