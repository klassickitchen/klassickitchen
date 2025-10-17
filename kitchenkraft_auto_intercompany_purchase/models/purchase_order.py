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
