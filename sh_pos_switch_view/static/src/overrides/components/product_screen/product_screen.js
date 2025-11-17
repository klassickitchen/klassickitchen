/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ShProductCard } from "@sh_pos_switch_view/overrides/components/product_screen/ShProductCard";

ProductScreen.components['ShProductCard'] = ShProductCard

patch(ProductScreen.prototype, {
    
    setup() {
        super.setup()
        onMounted(this.onMounted);
        this.pos = usePos();
    },
    onMounted() {
        console.log("on mount");
        
        if(this.pos.config.sh_pos_switch_view){
            if(this.pos.config.sh_default_view == 'grid_view'){
                document.getElementsByClassName('product_grid_view')[0].classList.add('highlight')
                // document.getElementsByClassName('sh_product_list_view')[0].classList.add('hide_sh_product_list_view')
            }
            if(this.pos.config.sh_default_view == 'list_view'){
                document.getElementsByClassName('product_list_view')[0].classList.add('highlight')
                document.getElementsByClassName('product-list')[1].classList.add('hide_product_list_container')
            }
        }
    }
});
