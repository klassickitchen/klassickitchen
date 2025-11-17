import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async setup(){
        await super.setup(...arguments)
        this.display_type_activated = this.config.sh_pos_switch_view ? this.config.sh_default_view : 'grid_view'
    },
});
