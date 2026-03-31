/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    async addProductToOrder(product) {

        const currentOrder = this.pos.get_order();
        const priceThreshold = 0.01;

        // Check if the search word matches a specific barcode record
        const searchWord = (this.pos.searchProductWord || "").trim();
        let barcodeRecord = null;

        if (searchWord) {
            try {
                const barcodeRecords = product["<-product.barcode.product_id"];
                if (barcodeRecords && barcodeRecords.length > 0) {
                    const currentCompanyId = this.pos.company.id;
                    barcodeRecord = barcodeRecords.find(
                        (b) => b.barcode === searchWord &&
                               (!b.company_id || (typeof b.company_id === 'object' ? b.company_id.id : b.company_id) === currentCompanyId)
                    );
                }
            } catch (_e) {
                // Silently ignore
            }
        }

        let customPrice;
        let customUom = null;

        if (barcodeRecord) {
            // Use barcode-specific price
            customPrice = barcodeRecord.price;

            // Use barcode-specific UOM
            if (barcodeRecord.uom_id) {
                const uomId = typeof barcodeRecord.uom_id === 'object' ? barcodeRecord.uom_id.id : barcodeRecord.uom_id;
                customUom = this.pos.data.models["uom.uom"]?.get(uomId);
                if (!customUom) {
                    console.warn("[product_screen_extension] Barcode UOM not found:", uomId);
                    customUom = product.uom_id;
                }
            }
        } else {
            // Fallback to product_price
            customPrice = product.product_price;
        }

        const productListPrice = product.lst_price || 0;

        // 1. Check if we need to apply custom logic
        const hasCustomPrice =
            customPrice !== undefined &&
            customPrice !== null &&
            (Math.abs(productListPrice - customPrice) > priceThreshold || customUom);

        if (hasCustomPrice) {
            const product_id = product.id;
            let merged = false;

            const lines = currentOrder.get_orderlines();

            // 2. Search for a mergeable existing line
            for (const line of lines) {
                if (line.get_product().id === product_id) {
                    // Check price match
                    const priceMatch = Math.abs(line.get_unit_price() - customPrice) < priceThreshold;
                    // Check UOM match
                    const lineUomId = line.custom_uom_id?.id || line.product_id.uom_id?.id;
                    const targetUomId = customUom?.id || product.uom_id?.id;
                    const uomMatch = lineUomId === targetUomId;

                    if (priceMatch && uomMatch) {
                        line.set_quantity(line.get_quantity() + 1);
                        merged = true;
                        break;
                    }
                }
            }

            // 3. If no mergeable line was found, add a new line with the custom price and UOM
            if (!merged) {
                const addLineVals = {
                    product_id: product,
                    product_tmpl_id: product.product_tmpl_id,
                    price_unit: customPrice,
                    price_type: "manual",
                };

                if (customUom) {
                    addLineVals.custom_uom_id = customUom;
                }

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