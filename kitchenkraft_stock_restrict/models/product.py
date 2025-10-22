from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    restrict_sell_out_of_stock = fields.Boolean(
        string="Restrict Out of Stock",
    )

    def _load_pos_data_fields(self, config_id):
        """Extend to include qty_available and virtual_available in POS data fields."""
        fields = super(ProductProduct, self)._load_pos_data_fields(config_id)
        if 'qty_available' not in fields:
            fields.append('qty_available')
        if 'restrict_sell_out_of_stock' not in fields:
            fields.append('restrict_sell_out_of_stock')
        return fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'product_uom_qty')
    def _check_stock_restriction(self):
        print('chhh')
        for line in self:
            product = line.product_id
            if (
                product.restrict_sell_out_of_stock
                and product.qty_available <= 0
            ):
                raise UserError(
                    f"Cannot sell '{product.display_name}' because it is out of stock "
                )


