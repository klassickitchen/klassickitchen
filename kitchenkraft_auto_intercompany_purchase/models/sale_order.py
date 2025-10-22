from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    intercompany_purchase_order_ids = fields.Many2many(
        'purchase.order',
        'sale_purchase_intercompany_rel',
        'sale_id', 'purchase_id',
        string='Intercompany POs',
        copy=False,
        readonly=True,
        help="Purchase Orders created automatically for intercompany stock transfer."
    )

    intercompany_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='First Intercompany PO',
        compute='_compute_first_po',
        store=True,
        readonly=True,
        help="First Purchase Order created automatically for intercompany stock transfer."
    )

    intercompany_po_count = fields.Integer(
        compute='_compute_intercompany_po_count',
        string="Intercompany PO Count"
    )

    @api.depends('intercompany_purchase_order_ids')
    def _compute_first_po(self):
        for order in self:
            order.intercompany_purchase_order_id = order.intercompany_purchase_order_ids[:1]

    @api.depends('intercompany_purchase_order_ids')
    def _compute_intercompany_po_count(self):
        for order in self:
            order.intercompany_po_count = len(order.intercompany_purchase_order_ids)

    def action_view_intercompany_po(self):
        self.ensure_one()
        if not self.intercompany_purchase_order_ids:
            return {}


        if len(self.intercompany_purchase_order_ids) == 1:
            action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = self.intercompany_purchase_order_ids[0].id
            return action


        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('id', 'in', self.intercompany_purchase_order_ids.ids)]
        return action

    def action_confirm(self):
        if self.env.context.get('skip_intercompany'):
            return super(SaleOrder, self).action_confirm()
        products_requiring_intercompany = []

        for order in self:

            stock_issues = False

            for line in order.order_line:
                product = line.product_id

                product_in_context = product.with_context(warehouse=order.warehouse_id.id)
                available_qty = product_in_context.qty_available


                outgoing_qty = product_in_context.outgoing_qty
                free_qty = available_qty - outgoing_qty if outgoing_qty else available_qty


                if free_qty < line.product_uom_qty:
                    stock_issues = True


                    required_qty = max(0, line.product_uom_qty - free_qty)


                    products_requiring_intercompany.append({
                        'product_id': product.id,
                        'quantity': required_qty,
                        'price_unit': product.standard_price,
                        'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
                    })


            if stock_issues and products_requiring_intercompany:

                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Create Intercompany Purchase Order'),
                    'res_model': 'intercompany.stock.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_sale_order_id': order.id,
                        'default_order_line_ids': [(0, 0, p) for p in products_requiring_intercompany]
                    },
                }

        return super(SaleOrder, self).action_confirm()
