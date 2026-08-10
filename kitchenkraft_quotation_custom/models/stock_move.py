from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_cost = fields.Float(string="Cost", compute='_compute_product_cost')
    product_sale_price = fields.Float(
        string="Sale Price",
        compute='_compute_product_sale_price',
        help="Unit price actually charged on the document behind this move: the sale "
             "order line for a delivery, the POS order line(s) for a POS transaction. "
             "Falls back to the product's sales price when there is no order behind "
             "the move, e.g. a manual internal transfer.",
    )
    @api.depends('product_id.standard_price', 'company_id')
    def _compute_product_cost(self):
        for move in self:
            move.product_cost = move.product_id.with_company(move.company_id).standard_price


    def _get_pos_sale_price(self):
        """Unit price charged in POS for this move's product, or None.

        Guarded on the registry because this module does not depend on
        point_of_sale: pos_order_id only exists once that app is installed.
        Read as sudo, since inventory users have no access to pos.order.line.

        POS merges every line of a same product into a single stock move (see
        stock.picking._create_move_from_pos_order_lines), so one move can cover
        several barcodes of that product sold at different prices. When those
        prices differ we return the quantity-weighted average, so that
        price * quantity still adds up to what was actually charged.
        """
        self.ensure_one()
        if 'pos.order' not in self.env:
            return None
        move = self.sudo()
        pos_order = move.picking_id.pos_order_id or move.group_id.pos_order_id
        if not pos_order:
            return None
        lines = pos_order.lines.filtered(lambda l: l.product_id == move.product_id)
        if not lines:
            return None
        prices = lines.mapped('price_unit')
        if len(set(prices)) == 1:
            return prices[0]
        total_qty = sum(abs(line.qty) for line in lines)
        if not total_qty:
            return sum(prices) / len(prices)
        return sum(line.price_unit * abs(line.qty) for line in lines) / total_qty

    @api.depends('product_id.product_price','company_id', 'sale_line_id.price_unit',
                 'picking_id', 'group_id')
    def _compute_product_sale_price(self):
        for move in self:
            # sudo: inventory users can read neither sale.order.line nor
            # pos.order.line, and they are the ones printing the delivery slip.
            sale_line = move.sudo().sale_line_id
            if sale_line:
                move.product_sale_price = sale_line.price_unit
                continue
            pos_price = move._get_pos_sale_price()
            move.product_sale_price = (
                move.product_id.with_company(move.company_id).product_price if pos_price is None else pos_price
            )
