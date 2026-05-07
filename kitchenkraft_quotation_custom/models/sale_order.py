from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # use_custom_description = fields.Boolean(string='Custom Description', default=False)
    show_product_image = fields.Boolean(string='Product Image', default=True)