from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier = fields.Char()
    country_id = fields.Many2one('res.country')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            barcode_record = self.env['product.barcode'].search([('barcode', '=', name)], limit=1)
            if barcode_record and barcode_record.product_id:
                product_variant = barcode_record.product_id
                product_template = product_variant.product_tmpl_id
                self.env['barcode.match'].store_match(
                    name,
                    product_variant.id,
                    barcode_record.uom_id.id,
                    barcode_record.price
                )
                result = [(product_template.id, product_variant.display_name)]
                return result

        return super().name_search(name, args, operator, limit)

    def get_single_product_variant(self):
        result = super().get_single_product_variant()
        match = self.env['barcode.match'].get_match()
        if self and match and match.product_id and match.product_id.product_tmpl_id.id == self.id:
            return {
                'product_id': match.product_id.id,
                'display_name': match.product_id.display_name,
            }

        return result


class BarcodeMatch(models.TransientModel):
    _name = 'barcode.match'
    _description = 'Barcode Match Storage'

    barcode = fields.Char()
    product_id = fields.Many2one('product.product')
    uom_id = fields.Many2one('uom.uom')
    price = fields.Float()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    create_date = fields.Datetime(default=fields.Datetime.now, index=True)

    @api.model
    def store_match(self, barcode, product_id, uom_id, price):
        user_id = self.env.user.id
        self.search([('user_id', '=', user_id)]).unlink()
        new_match = self.create({
            'barcode': barcode,
            'product_id': product_id,
            'uom_id': uom_id,
            'price': price,
        })
        return new_match

    @api.model
    def get_match(self):
        user_id = self.env.user.id
        match = self.search([('user_id', '=', user_id)], limit=1, order='create_date desc')
        return match
