from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # payment_type = fields.Selection(
    #     [('cash', 'Cash'),
    #      ('credit', 'Credit'),
    #      ], string='Cash|Credit',
    #     required=True
    # )