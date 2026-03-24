/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderWidget.prototype, {
    setup(){
        super.setup(...arguments);
        this.props["global_discount"] = 0.0
        this.pos = usePos();
    },
    pos_discount() {
        var order = this.pos.get_order();
        if (!order) return 0;
        // Always compute from orderlines so it survives refresh/navigation
        var orderlines = order.get_orderlines();
        if (orderlines && orderlines.length > 0) {
            var cumulative = 0;
            for (var i = 0; i < orderlines.length; i++) {
                var line = orderlines[i];
                if (line.discount > 0) {
                    cumulative += (line.price_unit * line.qty) - line.get_display_price();
                }
            }
            if (cumulative > 0) {
                // Keep the stored value in sync
                order.set_order_global_discount(cumulative);
                return cumulative.toFixed(2);
            }
        }
        return order.get_order_global_discount()
          ? parseFloat(order.get_order_global_discount()).toFixed(2)
          : 0;
    },
});
