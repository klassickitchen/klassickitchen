from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    alternative_barcode_ids = fields.One2many(
        "product.barcode",
        "product_id",
        string="Alternative Barcodes",
    )
