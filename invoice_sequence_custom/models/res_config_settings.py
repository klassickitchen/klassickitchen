from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_rounding_absorb = fields.Boolean(
        related='company_id.pos_rounding_absorb',
        readonly=False,
    )
    pos_rounding_absorb_threshold = fields.Monetary(
        related='company_id.pos_rounding_absorb_threshold',
        currency_field='currency_id',
        readonly=False,
    )
