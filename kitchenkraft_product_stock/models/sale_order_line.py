from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_view_stock_details(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Details',
            'view_mode': 'form',
            'res_model': 'stock.details.wizard',
            'target': 'new',
            'context': {
                'default_product_id': self.product_id.id,
                'default_company_id': self.order_id.company_id.id,
            },
        }