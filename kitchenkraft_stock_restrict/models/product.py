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

    def _load_pos_data(self, data):
        """Scope the POS On Hand / Forecasted figures to the till's own source location.

        Odoo computes qty_available with no location in the context, and
        stock/models/product.py:302 resolves that to *every warehouse of the active
        company*. For "Kitchenkraft- Showroom" that summed KK/SH and KK/WH together,
        so the product list advertised stock the till cannot sell (G1026 displayed 538
        while KK/SH/Stock actually held -12).

        Pinning the picking type's default source location makes the displayed figure
        equal the location the POS really decrements
        (point_of_sale/models/stock_picking.py:41). The location context matches by
        parent_path, so sub-locations such as KK/SH/Stock/4th Floor- Store are
        included automatically, and each config resolves its own location - no
        hard-coded ids.
        """
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        source_location = config.picking_type_id.default_location_src_id
        if source_location:
            self = self.with_context(location=source_location.id)
        return super(ProductProduct, self)._load_pos_data(data)


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


