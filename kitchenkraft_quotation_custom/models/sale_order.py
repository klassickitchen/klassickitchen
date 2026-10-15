from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # use_custom_description = fields.Boolean(string='Custom Description', default=False)
    show_product_image = fields.Boolean(string='Product Image', default=True)
    gross_total = fields.Monetary(
        string="Gross Total", currency_field='currency_id', compute='_compute_gross_discount'
    )
    amount_discount = fields.Monetary(
        string="Total Discount", currency_field='currency_id', compute='_compute_gross_discount'
    )

    @api.depends('order_line.amount_without_discount', 'amount_untaxed')
    def _compute_gross_discount(self):
        # Same approach as the invoice (invoice_sequence_custom): the discount is
        # Gross Total - Untaxed Amount, so the printed block always adds up instead of
        # summing per-line discounts that are rounded differently from price_subtotal.
        for order in self:
            order.gross_total = sum(order.order_line.mapped('amount_without_discount'))
            order.amount_discount = order.gross_total - order.amount_untaxed
