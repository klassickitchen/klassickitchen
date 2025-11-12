# models/pos_config.py
from odoo import models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def _get_pos_ui_product_product_fields(self):
        res = super()._get_pos_ui_product_product_fields()
        res += ["alternative_barcode_ids", "product_price"]
        return res

    def _get_pos_ui_uom_fields(self):
        res = super()._get_pos_ui_uom_fields()
        res += ["name"]
        return res
