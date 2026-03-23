/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(ControlButtons.prototype, {
    async onClickFixedDiscount() {
        const order = this.pos.get_order();
        if (!order || !order.get_orderlines() || order.get_orderlines().length === 0) {
            this.dialog.add(AlertDialog, {
                title: _t("No products"),
                body: _t("Add Product In Cart first."),
            });
            return;
        }

        this.dialog.add(NumberPopup, {
            title: _t("Fixed Discount"),
            startingValue: 0,
            getPayload: (num) => {
                const val = Math.max(0, this.env.utils.parseValidFloat(num.toString()));
                if (val > 0) {
                    this.applyFixedDiscount(val);
                }
            },
        });
    },

    async applyFixedDiscount(amount) {
        const order = this.pos.get_order();
        const lines = order.get_orderlines();
        const product = this.pos.config.discount_product_id;

        if (product === undefined) {
            this.dialog.add(AlertDialog, {
                title: _t("No discount product found"),
                body: _t(
                    "The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'. Please configure a discount product in POS settings."
                ),
            });
            return;
        }

        // Check if discount amount is greater than order total
        const orderTotal = order.get_total_with_tax();
        if (amount > orderTotal) {
            this.dialog.add(AlertDialog, {
                title: _t("Invalid discount"),
                body: _t("Discount amount cannot be greater than order total."),
            });
            return;
        }

        // Remove existing fixed discount lines (lines with discount product)
        lines.filter((line) => line.get_product() === product).forEach((line) => line.delete());

        // Add one discount line per tax group (similar to pos_discount module)
        const linesByTax = order.get_orderlines_grouped_by_tax_ids();
        const taxGroups = Object.keys(linesByTax);

        if (taxGroups.length === 1) {
            // Simple case: only one tax group, apply full discount
            const tax_ids = taxGroups[0];
            const tax_ids_array = tax_ids
                .split(",")
                .filter((id) => id !== "")
                .map((id) => Number(id));

            const taxes = tax_ids_array
                .map((taxId) => this.pos.models["account.tax"].get(taxId))
                .filter(Boolean);

            await this.pos.addLineToCurrentOrder(
                {
                    product_id: product,
                    price_unit: -amount,
                    tax_ids: [["link", ...taxes]]
                },
                { merge: false }
            );
        } else {
            // Multiple tax groups: distribute discount proportionally
            let totalBase = 0;
            for (const [tax_ids, taxLines] of Object.entries(linesByTax)) {
                const applicableLines = taxLines.filter((ll) => ll.isGlobalDiscountApplicable ? ll.isGlobalDiscountApplicable() : true);
                totalBase += order.calculate_base_amount ? order.calculate_base_amount(applicableLines) :
                    applicableLines.reduce((sum, line) => sum + line.get_display_price(), 0);
            }

            for (const [tax_ids, taxLines] of Object.entries(linesByTax)) {
                const tax_ids_array = tax_ids
                    .split(",")
                    .filter((id) => id !== "")
                    .map((id) => Number(id));

                const applicableLines = taxLines.filter((ll) => ll.isGlobalDiscountApplicable ? ll.isGlobalDiscountApplicable() : true);
                const baseAmount = order.calculate_base_amount ? order.calculate_base_amount(applicableLines) :
                    applicableLines.reduce((sum, line) => sum + line.get_display_price(), 0);

                const taxes = tax_ids_array
                    .map((taxId) => this.pos.models["account.tax"].get(taxId))
                    .filter(Boolean);

                // Proportional discount for this tax group
                const proportionalDiscount = totalBase > 0 ? (baseAmount / totalBase) * amount : 0;

                if (proportionalDiscount > 0) {
                    await this.pos.addLineToCurrentOrder(
                        {
                            product_id: product,
                            price_unit: -proportionalDiscount,
                            tax_ids: [["link", ...taxes]]
                        },
                        { merge: false }
                    );
                }
            }
        }
    },
});
