import logging # Import logging
from odoo import models, api, fields # Import fields if needed later



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.onchange('product_id')
    # def _onchange_barcode_product(self):
    #     """Set UOM and price when product is selected via barcode"""
    #
    #     if not self.product_id:
    #         return
    #
    #     match = self.env['barcode.match'].get_match()
    #
    #     if match and match.product_id.id == self.product_id.id:
    #         print(f"Applying barcode data to SOL for product {self.product_id.display_name} from barcode: {match.barcode}")
    #
    #         # --- Set UOM ---
    #         barcode_uom = match.uom_id
    #         product_default_uom = self.product_id.uom_id
    #
    #         if barcode_uom and barcode_uom.category_id == product_default_uom.category_id:
    #             print(f"Setting UOM to {barcode_uom.name} (ID: {barcode_uom.id}) from barcode match.")
    #             self.product_uom = barcode_uom.id
    #         elif barcode_uom:
    #             print(
    #                 f"Barcode UOM '{barcode_uom.name}' (Category: {barcode_uom.category_id.name}) "
    #                 f"is not compatible with Product '{self.product_id.name}' default UOM "
    #                 f"'{product_default_uom.name}' (Category: {product_default_uom.category_id.name}). "
    #                 f"UOM not changed."
    #             )
    #         else:
    #              print("No specific UOM found in barcode match. Standard UOM logic will apply.")
    #
    #
    #         # --- Set Price ---
    #         print(f"Setting Price Unit to {match.price} from barcode match.")
    #         self.price_unit = match.price
    #
    #
    #         print(f"Values before method exit: UOM ID = {self.product_uom.id}, Price Unit = {self.price_unit}")
    #
    #         print(f"Unlinking barcode match record {match.id}")
    #         match.unlink()
    #
    #     elif match:
    #          print(f"Ignoring barcode match {match.id} as product_id {self.product_id.id} does not match {match.product_id.id}.")
    #          # Decide if you want to unlink the irrelevant match here too
    #          # match.unlink()
    #
