/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { GlobalDiscountPopupWidget } from "@sh_pos_order_discount/apps/popups/GlobalDiscountPopupWidget/GlobalDiscountPopupWidget";
import {
    allocateFixedGlobalDiscount,
    previewPercentageGlobalDiscount,
} from "@sh_pos_order_discount/apps/popups/GlobalDiscountPopupWidget/discount_allocator";
import {
    DISCOUNT_DIGITS,
    quantizeDiscount,
} from "@sh_pos_show_discount/overrides/models/discount_precision";
import { useState, onMounted } from "@odoo/owl";

patch(GlobalDiscountPopupWidget.prototype, {
    setup() {
        super.setup(...arguments);
        const order = this.pos.get_order();
        const currentTotal = order ? order.get_total_with_tax() : 0;
        this.state = useState({
            equivDisplay: "0.00",
            amountBefore: currentTotal.toFixed(2),
            amountAfter: currentTotal.toFixed(2),
        });
        onMounted(() => {
            // Refresh amount before on mount in case order changed
            const order = this.pos.get_order();
            if (order) {
                this.state.amountBefore = order.get_total_with_tax().toFixed(2);
                this.state.amountAfter = order.get_total_with_tax().toFixed(2);
            }
        });
    },

    /**
     * Returns the current order total with tax.
     */
    _getOrderTotal() {
        const order = this.pos.get_order();
        if (!order) return 0;
        return order.get_total_with_tax();
    },

    /**
     * Called whenever the user types in the value input.
     * Computes the equivalent value and before/after amounts.
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
     * Core logic: compute equivalent discount value + before/after amounts.
     * If Fixed is selected  → show equivalent Percentage
     * If Percentage is selected → show equivalent Fixed Amount
     */
    _computeEquivalent(val) {
        const total = this._getOrderTotal();
        this.state.amountBefore = total.toFixed(2);

        if (!val || isNaN(val) || val <= 0) {
            this.state.equivDisplay = "0.00";
            this.state.amountAfter = total.toFixed(2);
            return;
        }

        const isFixed =
            document.getElementById("discount_fixed_radio") &&
            document.getElementById("discount_fixed_radio").checked;

        const order = this.pos.get_order();
        if (order && this.pos.is_global_discount) {
            // Run the exact same 2-decimal quantised allocator used by confirm()
            // so the popup preview always matches the cart total and posted invoice.
            if (isFixed) {
                const allocation = allocateFixedGlobalDiscount(order, val, DISCOUNT_DIGITS);
                this.state.equivDisplay = allocation.addedPct.toFixed(2) + " %";
                this.state.amountAfter = allocation.totalAfter.toFixed(2);
            } else {
                const preview = previewPercentageGlobalDiscount(order, val, DISCOUNT_DIGITS);
                this.state.equivDisplay = preview.addedDiscount.toFixed(2);
                this.state.amountAfter = preview.totalAfter.toFixed(2);
            }
            return;
        }

        // Fallback for per-line discount mode: single-line quantised preview.
        const pct = quantizeDiscount(isFixed ? (val / Math.abs(total)) * 100 : val);
        const discountAmount = (Math.abs(total) * pct) / 100;

        this.state.equivDisplay = isFixed
            ? pct.toFixed(2) + " %"
            : discountAmount.toFixed(2);
        this.state.amountAfter = (
            total < 0 ? total + discountAmount : total - discountAmount
        ).toFixed(2);
    },
});

