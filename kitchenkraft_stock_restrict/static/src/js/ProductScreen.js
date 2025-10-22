/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        console.log("js is loaded");
    },

    async addProductToOrder(product, options) {
        console.log("product:", product.display_name);
        const type = this.pos.config.stock_type;
        const restrictEnabled = product.restrict_sell_out_of_stock;
        const qty_available = product.qty_available || 0;

        console.log("Restriction Enabled:", restrictEnabled, "Qty:", qty_available);

        if (restrictEnabled && qty_available <= 0) {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Out of Stock"),
                body: _t("%s is out of stock and cannot be sold.", product.display_name),
                confirmLabel: _t("OK"),
            });
        } else {
            await super.addProductToOrder(product, options);
        }
    },

});
