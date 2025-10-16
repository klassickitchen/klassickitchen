
from odoo import fields, models

class PosConfig(models.Model):

    _inherit = 'pos.config'

    max_discount=fields.Float('Max Discount(%)')
    min_discount=fields.Float('Min Discount(%)')