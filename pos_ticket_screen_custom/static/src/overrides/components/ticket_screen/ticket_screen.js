/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // By default, if it's initialized to RECEIPT_NUMBER, swap it to our ALL search field
        // so it defaults to the two-way universal search
        if (this.state.search.fieldName === "RECEIPT_NUMBER" && !this.state.search.searchTerm) {
            this.state.search.fieldName = "ALL";
        }
    },

    _getSearchFields() {
        const fields = super._getSearchFields(...arguments);

        // Individual Invoice Number Search
        fields.INVOICE_NUMBER = {
            repr: (order) => {
                return order.account_move_name || '';
            },
            displayName: _t("Invoice Number"),
            modelField: "account_move_name",
        };

        // Individual Customer Mobile Search
        fields.CUSTOMER_NUMBER = {
            repr: (order) => {
                const p = order.get_partner();
                return p && p.mobile ? p.mobile : '';
            },
            displayName: _t("Customer Mobile"),
            modelField: "partner_id.mobile",
        };

        // Universal Supportable Search (Default)
        fields.ALL = {
            repr: (order) => {
                const p = order.get_partner();
                const mobile = p && p.mobile ? p.mobile : '';
                const invoice = order.account_move_name || '';
                const receipt = order.pos_reference || '';
                const tracking = order.tracking_number || '';
                return `${receipt} ${invoice} ${mobile} ${tracking}`;
            },
            displayName: _t("All (Receipt / Invoice / Mobile)"),
            modelField: "ALL", 
        };

        return fields;
    },

    _computeSyncedOrdersDomain() {
        let { fieldName, searchTerm } = this.state.search;
        if (!searchTerm) {
            return [];
        }

        // Handle the custom ALL routing
        if (fieldName === 'ALL') {
             return [
                '|',
                ['pos_reference', 'ilike', `%${searchTerm}%`],
                '|',
                ['account_move_name', 'ilike', `%${searchTerm}%`],
                ['partner_id.mobile', 'ilike', `%${searchTerm}%`],
            ];
        }

        return super._computeSyncedOrdersDomain(...arguments);
    }
});
