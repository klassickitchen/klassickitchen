from odoo import models, fields

class CrmTeam(models.Model):
    _inherit = "crm.team"

    analytic_plan_id = fields.Many2one('account.analytic.plan',string="Analytic Plan")
