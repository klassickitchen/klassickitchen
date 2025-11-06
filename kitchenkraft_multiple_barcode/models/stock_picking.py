from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"



    def _prepare_stock_move_vals(self, first_line, order_lines):
        return {
            'name': first_line.name,
            'product_uom': first_line.product_uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': first_line.product_id.id,
            'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'never_product_template_attribute_value_ids': first_line.attribute_value_ids.filtered(lambda a: a.attribute_id.create_variant == 'no_variant'),
        }