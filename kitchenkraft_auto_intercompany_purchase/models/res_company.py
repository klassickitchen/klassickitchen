from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    intercompany_margin_pct = fields.Float(
        string="Intercompany Margin (%)", 
        help="Margin added to the source company's cost during intercompany stock transfers."
    )
