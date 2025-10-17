from odoo import models

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def inter_company_create_sale_order(self, company):

        super(PurchaseOrderInherit, self).inter_company_create_sale_order(company)
        for rec in self:
            sale_orders = self.env['sale.order'].search([
                ('auto_purchase_order_id', '=', rec.id),
                ('state', 'in', ['draft', 'sent'])
            ])
            for so in sale_orders:
                so.action_confirm()
                for picking in so.picking_ids:
                    if picking.state not in ['assigned', 'confirmed']:
                        picking.action_assign()

                    if picking.state == 'assigned':
                        # Set qty_done to product_uom_qty to mark full delivery
                        for move_line in picking.move_line_ids:
                            move_line.qty_done = move_line.move_id.product_uom_qty

                        # Validate the delivery
                        picking.button_validate()
