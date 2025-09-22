from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    show_kitchen_kraft_report = fields.Boolean(compute="_compute_show_kitchen_kraft_report")

    @api.depends('company_id')
    def _compute_show_kitchen_kraft_report(self):
        for record in self:
            record.show_kitchen_kraft_report = record.company_id.id == 5
