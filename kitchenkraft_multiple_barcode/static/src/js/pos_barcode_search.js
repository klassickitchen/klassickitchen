/** @odoo-module **/

import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

console.log("[pos_barcode_search] JS file loaded");

/**
 * Patch 1: Include alternative barcodes (product.barcode) in local POS search.
 * Uses Odoo 18 reverse relation to access product.barcode records
 * linked to this product via the product_id Many2one field.
 */
patch(ProductProduct.prototype, {
    get searchString() {
        let base = super.searchString;
        try {
            const barcodeRecords = this["<-product.barcode.product_id"];
            if (barcodeRecords && barcodeRecords.length > 0) {
                const altBarcodes = barcodeRecords
                    .map((b) => b.barcode || "")
                    .filter(Boolean)
                    .join(" ");
                if (altBarcodes) {
                    base += " " + altBarcodes;
                }
            }
        } catch (_e) {
            // Silently ignore if reverse relation is not available
        }
        return base;
    },
});

console.log("[pos_barcode_search] ProductProduct searchString patch applied");

/**
 * Patch 2: Include alternative barcodes in the DB search domain.
 * When the user presses Enter in the POS search box, this adds
 * alternative_barcode_ids.barcode to the OR conditions so the
 * server also searches the product.barcode model.
 */
patch(ProductScreen.prototype, {
    loadProductFromDBDomain(searchProductWord) {
        console.log("[pos_barcode_search] loadProductFromDBDomain called with:", searchProductWord);
        return [
            "|",
            "|",
            "|",
            ["name", "ilike", searchProductWord],
            ["default_code", "ilike", searchProductWord],
            ["barcode", "ilike", searchProductWord],
            ["alternative_barcode_ids.barcode", "ilike", searchProductWord],
            ["available_in_pos", "=", true],
            ["sale_ok", "=", true],
        ];
    },
});

console.log("[pos_barcode_search] All patches applied");
