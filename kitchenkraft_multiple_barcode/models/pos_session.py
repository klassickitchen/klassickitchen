from odoo import api, models
from odoo.osv.expression import AND


class PosSession(models.Model):
    _inherit = 'pos.session'

    def find_product_by_barcode(self, barcode, config_id):
        product_fields = self.env['product.product']._load_pos_data_fields(config_id)
        product_packaging_fields = self.env['product.packaging']._load_pos_data_fields(config_id)
        product_context = {**self.env.context, 'display_default_code': False}

        # 1. Check product.barcode model
        product_barcode = self.env['product.barcode'].search([
            ('barcode', '=', barcode),
        ], limit=1)

        if product_barcode and product_barcode.product_id:
            result = {'product.product': product_barcode.product_id.with_context(product_context).read(product_fields,
                                                                                                       load=True)}
            if result['product.product']:
                result['product.product'][0]['uom_id'] = product_barcode.uom_id.id if product_barcode.uom_id else False
                result['product.product'][0]['lst_price'] = product_barcode.price
            return result

        # 2. Check product.product model
        product = self.env['product.product'].search([
            ('barcode', '=', barcode),
            ('sale_ok', '=', True),
            ('available_in_pos', '=', True),
        ])
        if product:
            return {'product.product': product.with_context(product_context).read(product_fields, load=False)}

        # 3. Check product.packaging model
        domain = [('barcode', '!=', False)]  # Changed to ensure barcode is not False or ''
        loaded_data = self._context.get('loaded_data')
        if loaded_data:
            loaded_product_ids = [x['id'] for x in loaded_data['product.product']]
            domain = AND([domain, [('product_id', 'in', [x['id'] for x in self._context.get('loaded_data')[
                'product.product']])]]) if self._context.get('loaded_data') else []
            domain = AND([domain, [('product_id', 'in', loaded_product_ids)]])
        packaging_params = {
            'search_params': {
                'domain': domain,
                'fields': ['name', 'barcode', 'product_id', 'qty'],
            },
        }
        packaging_params['search_params']['domain'] = [['barcode', '=', barcode]]
        packaging = self.env['product.packaging'].search(packaging_params['search_params']['domain'])

        if packaging and packaging.product_id:
            return {
                'product.product': packaging.product_id.with_context(product_context).read(product_fields, load=False),
                'product.packaging': packaging.read(product_packaging_fields, load=False)}
        else:
            return {
                'product.product': [],
                'product.packaging': [],
            }