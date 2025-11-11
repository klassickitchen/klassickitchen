/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    async addProductToOrder(product) {

        const currentOrder = this.pos.get_order();
        const customPrice = product.product_price;
        const productListPrice = product.lst_price || 0;
        const priceThreshold = 0.01;

        // 1. Check if we need to apply custom logic
        const hasCustomPrice =
            customPrice !== undefined &&
            customPrice !== null &&
            Math.abs(productListPrice - customPrice) > priceThreshold;

        if (hasCustomPrice) {
            const product_id = product.id;
            let merged = false;

            // --- FIX: Use the stable method to get the list of lines (Odoo 18/OWL) ---
            const lines = currentOrder.get_orderlines();
            // -----------------------------------------------------------------------

            // 2. Search for a mergeable existing line
            for (const line of lines) {
                // Check if the line is for the same product
                if (line.get_product().id === product_id) {
                    // Check for price match (using price threshold)
                    if (Math.abs(line.get_unit_price() - customPrice) < priceThreshold) {
                        // Found a mergeable line! Increase quantity.
                        line.set_quantity(line.get_quantity() + 1);
                        merged = true;
                        break;
                    }
                }
            }

            // 3. If no mergeable line was found, add a new line with the custom price
            if (!merged) {
                const addLineVals = {
                    product_id: product,
                    product_tmpl_id: product.product_tmpl_id,
                    price_unit: customPrice,
                    price_type: "manual",
                };

                let finalProduct = product;
                // Optional: Replicate configurable product logic
                if (this.searchWord && product.isConfigurable()) {
                    const barcode = this.searchWord;
                    const searchedProduct = product.variants.filter(
                        (p) => p.barcode && p.barcode.includes(barcode)
                    );
                    if (searchedProduct.length === 1) {
                        finalProduct = searchedProduct[0];
                        addLineVals.product_id = finalProduct;
                    }
                }

                await this.pos.addLineToCurrentOrder(
                    addLineVals,
                    {},
                    finalProduct.needToConfigure ? finalProduct.needToConfigure() : false
                );
            }

            return;
        }

        // 4. Fall back to original method
        await super.addProductToOrder(...arguments);
    }
});