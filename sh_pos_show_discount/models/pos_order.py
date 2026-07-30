# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)

# HALF-UP <-> HALF-DOWN, UP <-> DOWN
OPPOSITE_TIE_BREAK = {
    "UP": "DOWN",
    "DOWN": "UP",
    "HALF-UP": "HALF-DOWN",
    "HALF-DOWN": "HALF-UP",
}


class AccountCashRounding(models.Model):
    _inherit = "account.cash.rounding"

    def _mirrored_for_refund(self):
        """Same rounding step, opposite tie-break.

        POS inverts the tie-break itself whenever the amount still due is
        negative -- see getRoundedRemaining() in
        point_of_sale/static/src/app/models/pos_order.js -- so this is the rule
        the till actually applied when it paid a refund out.

        Returns an empty recordset if the method has no opposite (there is
        nothing to mirror for HALF-EVEN).
        """
        self.ensure_one()
        opposite = OPPOSITE_TIE_BREAK.get(self.rounding_method)
        if not opposite:
            return self.browse()

        mirrored = self.sudo().search([
            ("rounding", "=", self.rounding),
            ("rounding_method", "=", opposite),
            ("strategy", "=", self.strategy),
        ], limit=1)
        if mirrored:
            return mirrored

        # Created once, on the first refund, then reused. It inherits this
        # record's profit/loss accounts.
        return self.sudo().copy({
            "name": "%s (refunds)" % self.name,
            "rounding_method": opposite,
        })


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _should_round_invoice(self):
        """Mirror of shouldRound() in pos_order.js.

        _prepare_invoice_vals() in core sets invoice_cash_rounding_id
        unconditionally, while POS only rounds when this returns true. With
        "Only round cash method" enabled the invoice would round card and
        bank-transfer orders that the till left unrounded, producing the same
        collected-vs-invoiced mismatch on every non-cash order.
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

        if not self._should_round_invoice():
            vals["invoice_cash_rounding_id"] = False
            return vals

        # A refund that lands on an exact tie -- 3.50 against a 1 QAR step -- is
        # paid out by POS as 3.00 but invoiced by account.move as 4.00, because
        # account.move applies the configured method to the positive refund
        # total while POS inverted it. Point refunds at the mirrored record so
        # the credit note agrees with what left the drawer.
        if vals.get("move_type") == "out_refund" and vals.get("invoice_cash_rounding_id"):
            mirrored = self.config_id.rounding_method._mirrored_for_refund()
            if mirrored:
                vals["invoice_cash_rounding_id"] = mirrored.id
            else:
                _logger.warning(
                    "POS %s: cash rounding method %r has no opposite tie-break, "
                    "the credit note may be rounded away from the amount paid out.",
                    self.name, self.config_id.rounding_method.rounding_method,
                )
        return vals
