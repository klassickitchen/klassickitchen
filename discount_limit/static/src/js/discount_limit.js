/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
    async clickDiscount() {
        const posConfig = this.pos.config;
        const minDiscount = posConfig.min_discount || 0;
        const maxDiscount = posConfig.max_discount || 0;
        const utils = this.env.utils; // ✅ capture to avoid undefined context

        this.dialog.add(NumberPopup, {
            title: _t("Discount Percentage"),
            startingValue: this.pos.config.discount_pc,
            getPayload: (num) => {
                const val = Math.max(0, Math.min(100, utils.parseValidFloat(num.toString())));

                // 🔍 Validate: must be within [min, max]
                if (val < minDiscount || val > maxDiscount) {
                    this.dialog.add(AlertDialog, {
                        title: _t("Invalid Discount"),
                        body: _t(
                            `Discount must be between ${minDiscount}% and ${maxDiscount}% as per configuration.`
                        ),
                    });
                    return;
                }

                // ✅ Within range — apply the discount
                this.apply_discount(val);
            },
        });
    },
});
