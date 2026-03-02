/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { GlobalDiscountPopupWidget } from "@sh_pos_order_discount/apps/popups/GlobalDiscountPopupWidget/GlobalDiscountPopupWidget";
import { useState } from "@odoo/owl";

patch(GlobalDiscountPopupWidget.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            equivDisplay: "0.00",
        });
    },

    /**
     * Returns the current order total with tax.
     * If a global discount was already applied, it resets discounts
     * temporarily to get the "clean" total.
     */
    _getOrderTotal() {
        const order = this.pos.get_order();
        if (!order) return 0;
        return order.get_total_with_tax();
    },

    /**
     * Called whenever the user types in the value input.
     * Computes the equivalent value for the other discount type.
     */
    onValueInput(ev) {
        const val = parseFloat(ev.target.value);
        this._computeEquivalent(val);
    },

    /**
     * Called when user switches between Fixed / Percentage radio.
     * Re-compute equivalent based on current input value.
     */
    onRadioChange() {
        const inputEl = document.querySelector(".sh_discount_value");
        const val = inputEl ? parseFloat(inputEl.value) : 0;
        this._computeEquivalent(val);
    },

    /**
     * Core logic: compute equivalent discount value.
     * If Fixed is selected  → show equivalent Percentage
     * If Percentage is selected → show equivalent Fixed Amount
     */
    _computeEquivalent(val) {
        if (!val || isNaN(val) || val <= 0) {
            this.state.equivDisplay = "0.00";
            return;
        }

        const total = this._getOrderTotal();
        const isFixed =
            document.getElementById("discount_fixed_radio") &&
            document.getElementById("discount_fixed_radio").checked;

        if (isFixed) {
            // Fixed entered → show equivalent percentage
            if (total > 0) {
                const pct = (val / total) * 100;
                this.state.equivDisplay = pct.toFixed(2) + " %";
            } else {
                this.state.equivDisplay = "0.00 %";
            }
        } else {
            // Percentage entered → show equivalent fixed amount
            if (total > 0) {
                const fixed = (total * val) / 100;
                this.state.equivDisplay = fixed.toFixed(2);
            } else {
                this.state.equivDisplay = "0.00";
            }
        }
    },
});

