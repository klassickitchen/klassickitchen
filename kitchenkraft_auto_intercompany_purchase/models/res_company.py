from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    intercompany_margin_pct = fields.Float(
        string="Intercompany Margin (%)", 
        help="Margin added to the source company's cost during intercompany stock transfers."
    )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Allow the intercompany wizard to see all companies regardless of user access."""
        if self.env.context.get('intercompany_wizard_search'):
            return self.sudo().with_context(intercompany_wizard_search=False).name_search(
                name, args, operator, limit
            )
        return super().name_search(name, args, operator, limit)
