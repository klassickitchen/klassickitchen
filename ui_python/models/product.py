from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"
    #
    # @api.model
    # def create(self, vals):
    #     context = self.env.context
    #     if 'barcode' in context:
    #         vals['barcode'] = context.get('barcode')
    #     if 'lst_price' in context:
    #         vals['lst_price'] = context.get('lst_price')
    #     if 'standard_price' in context:
    #         vals['standard_price'] = context.get('standard_price')
    #     if 'default_code' in context:
    #         vals['default_code'] = context.get('default_code')
    #     if 'description_sale' in context:
    #         vals['description_sale'] = context.get('description_sale')
    #     return super(ProductProduct, self).create(vals)
