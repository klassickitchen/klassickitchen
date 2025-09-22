from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    show_al_saif_report = fields.Boolean(compute="_compute_show_al_saif_report")

    @api.depends('company_id')
    def _compute_show_al_saif_report(self):
        for record in self:
            record.show_al_saif_report = record.company_id.id == 2
