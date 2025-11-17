from odoo import _, api, fields, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _load_pos_data_fields(self, config_id):
        result =super()._load_pos_data_fields(config_id)
        result +=  [
            'qty_available','virtual_available','product_variant_count'
        ]
        return result
