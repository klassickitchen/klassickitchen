# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    """ Add sequence numbers to invoice lines """
    _inherit = 'account.move.line'

    invoice_sequence_number = fields.Char(string='No.  ', compute="_compute_invoice_line_sequence")

    @api.depends('invoice_sequence_number')
    def _compute_invoice_line_sequence(self):
        number = 1
        for record in self.move_id.invoice_line_ids:
            record.invoice_sequence_number = number
            number += 1
