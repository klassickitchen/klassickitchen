from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_order_line_product_image = fields.Image(string='Product Image')
    amount_without_discount = fields.Monetary(
        string="Amount Before Discount",
        currency_field='currency_id',
        compute='_compute_amount_without_discount',
    )

    @api.depends('product_uom_qty', 'price_unit', 'display_type', 'product_id.is_discount')
    def _compute_amount_without_discount(self):
        # Discount product lines are left out of the gross, so their amount ends up in
        # the order's Discount (Gross Total - Untaxed Amount) rather than as a line.
        for line in self:
            line.amount_without_discount = (
                0.0 if line.display_type or line.product_id.is_discount
                else line.price_unit * line.product_uom_qty
            )

    # custom_description = fields.Char(string='Custom Description')

    @api.onchange('product_id')
    def auto_sale_order_line_product_image(self):
        for order in self:
            if order.product_id and order.product_id.image_1920:
                order.sale_order_line_product_image = order.product_id.image_1920
            elif order.product_template_id.image_1920:
                order.sale_order_line_product_image = order.product_template_id.image_1920