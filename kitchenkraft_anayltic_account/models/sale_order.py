from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.user_id and order.user_id.analytic_account_id:
                analytic_account = order.user_id.analytic_account_id
                for line in order.order_line:
                    line.analytic_distribution = {
                        analytic_account.id: 100.0
                    }
        return res



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        for rec in res:
            sale_order = self.env['sale.order'].search([("name", "=", rec.move_id.invoice_origin)], limit=1)
            if sale_order and sale_order.analytic_account_id and sale_order.analytic_account_id.name == "view":
                json_data = {
                    sale_order.analytic_account_id.id: 100
                }
                rec.analytic_distribution = json_data
        return res











