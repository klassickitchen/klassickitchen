from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    supplier = fields.Char(string="Supplier")
    country_id = fields.Many2one("res.country")
    alternative_barcode_ids = fields.One2many(
        "product.barcode",
        "product_id",
        string="Alternative Barcodes",
    )
