from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    analytic_account_id = fields.Many2one('account.analytic.account', string="Default Analytic Account")
