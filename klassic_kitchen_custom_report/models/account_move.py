from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    show_klassic_kitchen_report = fields.Boolean(compute="_compute_show_klassic_kitchen_report")

    @api.depends('company_id')
    def _compute_show_klassic_kitchen_report(self):
        for record in self:
            record.show_klassic_kitchen_report = record.company_id.id == 1
