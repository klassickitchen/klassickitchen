# -*- coding: utf-8 -*-
from odoo import models, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    account_move_name = fields.Char(related='account_move.name', string='Invoice Number Name', store=True)
