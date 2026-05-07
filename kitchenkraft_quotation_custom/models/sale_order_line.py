from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_order_line_product_image = fields.Image(string='Product Image')

    # custom_description = fields.Char(string='Custom Description')

    @api.onchange('product_id')
    def auto_sale_order_line_product_image(self):
        for order in self:
            if order.product_id and order.product_id.image_1920:
                order.sale_order_line_product_image = order.product_id.image_1920
            elif order.product_template_id.image_1920:
                order.sale_order_line_product_image = order.product_template_id.image_1920