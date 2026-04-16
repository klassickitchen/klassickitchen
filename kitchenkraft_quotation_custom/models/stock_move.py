from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_cost = fields.Float(string="Cost", related='product_id.standard_price')
    product_sale_price = fields.Float(string="Sale Price", related='product_id.list_price')