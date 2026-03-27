import { Component , reactive} from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ShProductCard extends Component {
    static template = "sh_pos_switch_view.ShProductCard";
    static props = {
        class: { String, optional: true },
        name: String,
        product: Object,
        productId: Number | String,
        comboExtraPrice: { String, optional: true },
        color: { type: [Number, undefined], optional: true },
        imageUrl: [String, Boolean],
        productInfo: { Boolean, optional: true },
        onClick: { type: Function, optional: true },
        onProductInfoClick: { type: Function, optional: true },
        showWarning: { type: Boolean, optional: true },
        productCartQty: { type: [Number, undefined], optional: true },
        // default_code: { type: [Number, String,undefined], optional: true },
    };
    static defaultProps = {
        onClick: () => {},
        onProductInfoClick: () => {},
        class: "",
        showWarning: false,
    };

    get productQty() {
        return this.env.utils.formatProductQty(this.props.productCartQty ?? 0, false);
    }

    setup() {
        super.setup();
        this.pos = usePos();
    }

    /**
     * Find the matching product.barcode record for the current search word.
     * Returns the barcode record or null.
     */
    _findMatchingBarcodeRecord(product) {
        const searchWord = (this.pos.searchProductWord || "").trim();
        if (!searchWord) {
            return null;
        }
        try {
            // Access the product.barcode records linked to this product via reverse relation
            const barcodeRecords = product["<-product.barcode.product_id"];
            if (barcodeRecords && barcodeRecords.length > 0) {
                const currentCompanyId = this.pos.company.id;
                const match = barcodeRecords.find(
                    (b) => b.barcode === searchWord &&
                           (!b.company_id || (typeof b.company_id === 'object' ? b.company_id.id : b.company_id) === currentCompanyId)
                );
                if (match) {
                    return match;
                }
            }
        } catch (_e) {
            // Silently ignore if reverse relation is not available
        }
        return null;
    }

    /**
     * Get the price to display in the table for this product.
     * If the search word matches a specific barcode record, return that barcode's price.
     * Otherwise, return the default product_price.
     */
    getBarcodePrice(product) {
        const barcodeRecord = this._findMatchingBarcodeRecord(product);
        if (barcodeRecord && barcodeRecord.price !== undefined) {
            return barcodeRecord.price;
        }
        // Fallback to product_price or lst_price
        return product.product_price ?? product.lst_price ?? 0;
    }

    async addProductToOrder(product) {

        const currentOrder = this.pos.get_order();
        const priceThreshold = 0.01;

        // Check if search word matches a specific barcode record
        const barcodeRecord = this._findMatchingBarcodeRecord(product);

        let priceToUse;
        let customUom = null;

        if (barcodeRecord) {
            // Use barcode-specific price
            priceToUse = Number(barcodeRecord.price ?? product.product_price ?? product.lst_price ?? 0);

            // Use barcode-specific UOM
            if (barcodeRecord.uom_id) {
                const uomId = typeof barcodeRecord.uom_id === 'object' ? barcodeRecord.uom_id.id : barcodeRecord.uom_id;
                customUom = this.pos.data.models["uom.uom"]?.get(uomId);
                if (!customUom) {
                    console.warn("[ShProductCard] Barcode UOM not found in POS data:", uomId);
                }
            }
        } else {
            // Fallback to product_price
            const customPrice = product.product_price;
            priceToUse = Number(customPrice ?? product.lst_price ?? 0);
        }

        const hasCustomPrice = Math.abs(priceToUse - (product.lst_price || 0)) > priceThreshold || customUom;

        // --- Merge logic ---
        if (hasCustomPrice) {
            let merged = false;
            const productId = product.id;
            const lines = currentOrder.get_orderlines();

            for (const line of lines) {
                if (line.get_product().id === productId) {
                    // Check price match
                    const priceMatch = Math.abs(line.get_unit_price() - priceToUse) < priceThreshold;
                    // Check UOM match
                    const lineUomId = line.custom_uom_id?.id || line.product_id.uom_id?.id;
                    const targetUomId = customUom?.id || product.uom_id?.id;
                    const uomMatch = lineUomId === targetUomId;

                    if (priceMatch && uomMatch) {
                        // Merge: increase quantity
                        line.set_quantity(line.get_quantity() + 1);
                        merged = true;
                        break;
                    }
                }
            }

            // If not merged → create new line
            if (!merged) {
                const addLineVals = {
                    product_id: product,
                    product_tmpl_id: product.product_tmpl_id,
                    price_unit: priceToUse,
                    price_type: "manual",
                };
                if (customUom) {
                    addLineVals.custom_uom_id = customUom;
                }
                await this.pos.addLineToCurrentOrder(addLineVals);
            }

            return;
        }

        // No custom price -> normal add
        await this.pos.addLineToCurrentOrder({
            product_id: product,
            price_unit: priceToUse,
        });
    }

}
