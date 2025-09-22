import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";


patch(PosOrder.prototype, {

    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        if (this.partner_id){
            result.headerData.customer_name = this.partner_id.name;
        }
        return result;
    },
});