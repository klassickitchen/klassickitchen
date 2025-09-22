from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    show_aldiyafa_report = fields.Boolean(compute="_compute_show_aldiyafa_report")

    @api.depends('company_id')
    def _compute_show_aldiyafa_report(self):
        for record in self:
            record.show_aldiyafa_report = record.company_id.id == 3
