/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";

patch(OrderWidget.prototype, {
    get_return_qty() {
        var order = this.pos.get_order();
        if (!order) return 0;
        var orderlines = order.get_orderlines();
        var total = 0;
        for (let i = 0; i < orderlines.length; i++) {
            if (orderlines[i].qty < 0) {
                total += Math.abs(orderlines[i].qty);
            }
        }
        return total;
    },
    get_zero_qty() {
        var order = this.pos.get_order();
        if (!order) return 0;
        return order.get_orderlines().filter(line => line.qty === 0).length;
    },
    get_items_qty() {
        var order = this.pos.get_order();
        if (!order) return 0;
        var orderlines = order.get_orderlines();
        var total = 0;
        for (let i = 0; i < orderlines.length; i++) {
            if (orderlines[i].qty > 0) {
                total += orderlines[i].qty;
            }
        }
        return total;
    }
});
