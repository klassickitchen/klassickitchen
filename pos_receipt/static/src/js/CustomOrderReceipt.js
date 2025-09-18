/** @odoo-module**/

import { Component } from "@odoo/owl";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline"; // Corrected import
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget"; // Corrected import
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header"; // Corrected import and component name
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt"; // Corrected import
import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen"; // Corrected import
import { omit } from "@web/core/utils/objects";

export class CustomOrderReceipt extends OrderReceipt {
    static template = "OrderReceipt";  // Corrected template name

    static components = {
        Orderline,
        OrderWidget,
        ReceiptHeader,
    };

    static props = {
        data: Object,
        formatCurrency: Function,
        basic_receipt: { type: Boolean, optional: true },
    };

    static defaultProps = {
        basic_receipt: false,
    };

    omit(...args){
        return omit(...args);
    }

    doesAnyOrderlineHaveTaxLabel() {
        return this.props.data.orderlines.some((line) => line.taxGroupLabels);
    }
}

patch(ReceiptScreen, {
        components: { ...ReceiptScreen.components, CustomOrderReceipt },
});