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
        await reactive(this.pos).addLineToCurrentOrder({ product_id: product }, {});
    }
}
