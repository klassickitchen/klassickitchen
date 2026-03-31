from odoo import http, _
from odoo.http import request
from odoo.osv import expression

try:
    from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController
except ImportError:
    StockBarcodeController = None


if StockBarcodeController:
    class StockBarcodeControllerInherit(StockBarcodeController):

        @http.route()
        def main_menu(self, barcode, **kw):
            return super().main_menu(barcode, **kw)

        def _try_open_product_location(self, barcode):
            """Extend to also search product.barcode model."""
            result = super()._try_open_product_location(barcode)
            if result:
                return result
            # Fallback: search in custom product.barcode model with company filter
            current_company = request.env.company.id
            barcode_records = request.env['product.barcode'].search([
                ('barcode', '=', barcode),
                ('company_id', '=', current_company),
            ])
            if barcode_records:
                product = barcode_records[0].product_id
                tree_view_id = request.env.ref('stock.view_stock_quant_tree').id
                kanban_view_id = request.env.ref('stock_barcode.stock_quant_barcode_kanban_2').id
                return {
                    'action': {
                        'name': product.display_name,
                        'res_model': 'stock.quant',
                        'views': [(tree_view_id, 'list'), (kanban_view_id, 'kanban')],
                        'type': 'ir.actions.act_window',
                        'domain': [('product_id', '=', product.id)],
                        'context': {
                            'search_default_internal_loc': True,
                        },
                    }
                }
            return False

        @http.route('/stock_barcode/get_specific_barcode_data', type='json', auth='user')
        def get_specific_barcode_data(self, **kwargs):
            """Extend to also search product.barcode model for product lookups."""
            result = super().get_specific_barcode_data(**kwargs)

            # Check if we already found product records
            has_products = False
            if isinstance(result, dict):
                product_records = result.get('product.product', [])
                if product_records:
                    has_products = True

            # If no product found, search in product.barcode model
            if not has_products:
                barcodes_by_model = kwargs.get('barcodes_by_model', {})
                product_barcodes = barcodes_by_model.get('product.product', [])
                single_barcode = kwargs.get('barcode') or kwargs.get('barcodes')

                barcodes_to_search = []
                if product_barcodes:
                    barcodes_to_search = product_barcodes
                elif single_barcode:
                    if isinstance(single_barcode, list):
                        barcodes_to_search = single_barcode
                    else:
                        barcodes_to_search = [single_barcode]

                if barcodes_to_search:
                    current_company = request.env.company.id
                    alt_barcode_records = request.env['product.barcode'].search([
                        ('barcode', 'in', barcodes_to_search),
                        ('company_id', '=', current_company),
                    ])
                    print("alt_barcode_records", alt_barcode_records)
                    print("current_company", current_company)
                    print("product name",alt_barcode_records.mapped('product_id').name)
                    if alt_barcode_records:
                        products = alt_barcode_records.mapped('product_id')
                        if products:
                            fetched_data = self._get_records_fields_stock_barcode(products)
                            if isinstance(result, dict):
                                for model_name, records in fetched_data.items():
                                    if model_name in result:
                                        existing_ids = {r['id'] for r in result[model_name]}
                                        for rec in records:
                                            if rec['id'] not in existing_ids:
                                                result[model_name].append(rec)
                                    else:
                                        result[model_name] = records
                                # Set the alternative barcode on the product data so JS cache can match it
                                for alt_bc in alt_barcode_records:
                                    for product_data in result.get('product.product', []):
                                        if product_data['id'] == alt_bc.product_id.id:
                                            if not product_data.get('barcode'):
                                                product_data['barcode'] = alt_bc.barcode
            return result
