from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_discount = fields.Boolean(string='Is Discount', default=False)