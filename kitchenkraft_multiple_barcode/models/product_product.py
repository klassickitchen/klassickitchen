from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    alternative_barcode_ids = fields.One2many('product.barcode', 'product_id', string='Alternative Barcodes')
    #
    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     """Override to search by barcode in product.barcode model"""
    #     args = args or []
    #     domain = []
    #
    #     if name and operator == 'ilike':
    #         # Store the barcode in context for later use
    #         self = self.with_context(possible_barcode=name)
    #
    #         # Try to find a product by barcode in product.barcode model
    #         barcode_records = self.env['product.barcode'].search([('barcode', '=', name)])
    #         if barcode_records:
    #             product_ids = barcode_records.mapped('product_id.id')
    #             domain = [('id', 'in', product_ids)]
    #             return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
    #
    #     return super(ProductProduct, self)._name_search(name, args=args, operator=operator,
    #                                                     limit=limit, name_get_uid=name_get_uid)