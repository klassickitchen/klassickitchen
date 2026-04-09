from odoo import models,fields
# class ReportProductLabelAllBarcodes(models.AbstractModel):
#     _inherit = 'report.product.report_producttemplatelabel2x7' #inheriting only the 2x7 only
#
#     def _get_report_values(self, docids, data):
#         result = super()._get_report_values(docids, data) #all the product related
#         quantity_by_product = result.get('quantity', {})
#
#         # Add alternative barcodes
#         for product, barcodes in list(quantity_by_product.items()):#iterate through each product return each product and barcode
#             if hasattr(product, 'alternative_barcode_ids'):#if only there are more barcodes
#                 for alt in product.alternative_barcode_ids:
#                     quantity_by_product[product].append((alt.barcode, 1)) #1 is default appending each barcodes
#
#         result['quantity'] = quantity_by_product
#         return result
# class ReportProductLabelDymoBarcodes(models.AbstractModel):
#     _inherit = 'report.product.report_producttemplatelabel_dymo' #inheriting only the dymo only
#
#
#
#
#     def _get_report_values(self, docids, data):
#         result = super()._get_report_values(docids, data)
#         quantity_by_product = result.get('quantity', {})
#
#         # Add alternative barcodes with price
#         for product, barcodes in list(quantity_by_product.items()):
#             if hasattr(product, 'alternative_barcode_ids'):
#                 for alt in product.alternative_barcode_ids:
#                     # Ensure quantity is integer
#                     print('barcodes',barcodes)
#                     qty = 1
#                     if barcodes and isinstance(barcodes[0][1], (int, float, str)):
#                         try:
#                             qty = int(float(barcodes[0][1]))
#                         except Exception:
#                             qty = 1
#
#
#                     quantity_by_product[product].append((alt.barcode, qty, alt.price))
#
#         result['quantity'] = quantity_by_product
#         print('result', result)
#         return result
#

class ReportProductLabelDymoBarcodes(models.AbstractModel):
    _inherit = 'report.product.report_producttemplatelabel_dymo' #inheriting only the dymo only

    def _get_report_values(self, docids, data):
        result = super()._get_report_values(docids, data)
        quantity_by_product = result.get('quantity', {})

        ctx = self.env.context

        if ctx.get('from_alternative_barcode') and ctx.get('default_barcode'):
            default_barcode = ctx['default_barcode']

            for product in quantity_by_product.keys():

                alt = product.alternative_barcode_ids.filtered(
                    lambda b: b.barcode == default_barcode
                )

                if alt:
                    alt_record = alt[0]
                    quantity_by_product[product] = [(alt_record.barcode, 1, alt_record.price)]

                else:
                    variants = product.product_variant_ids if hasattr(product, 'product_variant_ids') else [product]
                    matched_variant = None
                    for variant in variants:
                        if variant.barcode == default_barcode:
                            matched_variant = variant
                            break

                    if matched_variant:
                        quantity_by_product[product] = [(matched_variant.barcode, 1, matched_variant.lst_price)]

                    else:
                        found = False
                        for variant in variants:
                            alt_on_variant = variant.alternative_barcode_ids.filtered(
                                lambda b: b.barcode == default_barcode
                            )
                            if alt_on_variant:
                                alt_record = alt_on_variant[0]
                                quantity_by_product[product] = [(alt_record.barcode, 1, alt_record.price)]
                                found = True
                                break

                        if not found:
                            quantity_by_product[product] = []

            result['quantity'] = quantity_by_product

            for prod, barcodes in result['quantity'].items():
                print(f"  {prod.name} => {barcodes}")

        return result






