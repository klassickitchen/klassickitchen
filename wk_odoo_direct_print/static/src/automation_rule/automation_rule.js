/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// Wait for the base field to be registered, then extend it
const fieldsRegistry = registry.category("fields");

// Use onAdd hook or defer the extension
setTimeout(() => {
    const originalField = fieldsRegistry.get("base_automation_actions_one2many");
    
    if (!originalField) {
        console.warn("base_automation_actions_one2many field not found");
        return;
    }

    class ExtendedActionsOne2ManyField extends originalField.component {
        static actionStates = {
            ...originalField.component.actionStates,
            auto_print: _t("Automatic Printing"),
        };

        getPrinterName(action) {
            console.log('testing', action);
            return action.data.printer_id ? action.data.printer_id[1] : "";
        }

        getReportName(action) {
            return action.data.report_id ? action.data.report_id[1] : "";
        }
    }

    fieldsRegistry.add("base_automation_actions_one2many", {
        ...originalField,
        component: ExtendedActionsOne2ManyField,
        relatedFields: [
            ...originalField.relatedFields,
            { name: "printer_id", type: "many2one" },
            { name: "report_id", type: "many2one" },
        ],
    }, { force: true });
}, 0);