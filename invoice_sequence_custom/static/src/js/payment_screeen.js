/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    onMounted() {
        super.onMounted && super.onMounted();

        const order = this.pos.get_order();
        if (order) {
            order.set_to_invoice(true);
        }
    },
});
