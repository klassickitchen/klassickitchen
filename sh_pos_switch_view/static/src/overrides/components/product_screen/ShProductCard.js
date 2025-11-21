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
    async addProductToOrder(product) {

        const currentOrder = this.pos.get_order();

        // Always use product.product_price when present
        const customPrice = product.product_price;
        const priceToUse = Number(customPrice ?? product.lst_price ?? 0);
        const priceThreshold = 0.01;

        const hasCustomPrice = customPrice !== undefined && customPrice !== null;

        // --- Merge logic ---
        if (hasCustomPrice) {
            let merged = false;
            const productId = product.id;
            const lines = currentOrder.get_orderlines();

            for (const line of lines) {
                if (line.get_product().id === productId) {
                    if (Math.abs(line.get_unit_price() - priceToUse) < priceThreshold) {
                        // Merge: increase quantity
                        line.set_quantity(line.get_quantity() + 1);
                        merged = true;
                        break;
                    }
                }
            }

            // If not merged → create new line
            if (!merged) {
                await this.pos.addLineToCurrentOrder({
                    product_id: product,
                    product_tmpl_id: product.product_tmpl_id,
                    price_unit: priceToUse,
                    price_type: "manual",
                });
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
