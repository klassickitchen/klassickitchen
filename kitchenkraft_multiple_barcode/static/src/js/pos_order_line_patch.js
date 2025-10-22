/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
  setup(vals) {
    super.setup(vals);
    if (vals.custom_uom_id && !this.custom_uom_id) {
      this.custom_uom_id = vals.custom_uom_id;
    }
  },

  get_unit() {
    return this.custom_uom_id || this.product_id.uom_id;
  },

  get_quantity_str_with_unit() {
    const unit = this.custom_uom_id || this.product_id.uom_id;
    if (this.is_pos_groupable()) {
      return this.quantityStr + " " + unit.name;
    } else {
      return this.quantityStr;
    }
  },

  is_pos_groupable() {
    const unit = this.custom_uom_id || this.product_id.uom_id;
    const unit_groupable = unit ? unit.is_pos_groupable : false;
    return unit_groupable && !this.isPartOfCombo();
  },

  can_be_merged_with(orderline) {
    if (this.skip_change) {
      return false;
    }

    if (orderline.getNote() !== this.getNote()) {
      return false;
    }

    if (this.get_product().id !== orderline.get_product().id) {
      return false;
    }

    if (!this.is_pos_groupable()) {
      return false;
    }

    const thisUomId = this.custom_uom_id?.id || this.product_id.uom_id?.id;
    const otherUomId =
      orderline.custom_uom_id?.id || orderline.product_id.uom_id?.id;

    if (thisUomId !== otherUomId) {
      return false;
    }

    const priceThreshold = 0.01;
    const thisPrice = this.get_unit_price();
    const otherPrice = orderline.get_unit_price();

    if (Math.abs(thisPrice - otherPrice) > priceThreshold) {
      return false;
    }

    if (this.get_discount() !== 0 || orderline.get_discount() !== 0) {
      return false;
    }

    if (this.isLotTracked()) {
      return false;
    }

    const isSameCustomerNote =
      (Boolean(orderline.get_customer_note()) === false &&
        Boolean(this.get_customer_note()) === false) ||
      orderline.get_customer_note() === this.get_customer_note();

    if (!isSameCustomerNote) {
      return false;
    }

    if (this.refunded_orderline_id || orderline.isPartOfCombo()) {
      return false;
    }

    return true;
  },

  getDisplayData() {
    const data = super.getDisplayData();

    const unit = this.custom_uom_id || this.product_id.uom_id;
    const oldUnit = data.unit;
    data.unit = unit ? unit.name : "";

    if (this.custom_uom_id) {
    }

    return data;
  },

  serialize(options = {}) {
    const data = super.serialize(options);

    if (this.custom_uom_id && options.orm) {
      data.product_uom_id = this.custom_uom_id.id;
    } else if (!data.product_uom_id && this.product_id.uom_id && options.orm) {
      data.product_uom_id = this.product_id.uom_id.id;
    }

    return data;
  },
});
