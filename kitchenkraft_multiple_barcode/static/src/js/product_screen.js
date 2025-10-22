/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
  async _barcodeProductAction(code) {
    const product = await this._getProductByBarcode(code);

    if (!product) {
      this.sound?.play("error");
      this.barcodeReader.showNotFoundNotification(code);
      return;
    }
    const hasCustomBarcodeData =
      product._barcode_uom_id !== undefined ||
      product._barcode_price !== undefined;

    if (hasCustomBarcodeData) {
      await this._addProductWithCustomBarcode(product, code);
    } else {
      await this.pos.addLineToCurrentOrder(
        { product_id: product, product_tmpl_id: product.product_tmpl_id },
        { code },
        product.needToConfigure ? product.needToConfigure() : false
      );
    }

    this.numberBuffer.reset();
  },

  async _addProductWithCustomBarcode(product, code) {
    const customUomId = product._barcode_uom_id;
    const customPrice = product._barcode_price;

    try {
      let customUom = null;
      if (customUomId) {
        customUom = this.pos.data.models["uom.uom"]?.get(customUomId);
        if (!customUom) {
          console.warn("Custom UOM not found in POS data:", customUomId);
          customUom = product.uom_id;
        }
      }

      const addLineVals = {
        product_id: product,
        product_tmpl_id: product.product_tmpl_id,
      };

      if (customUom) {
        addLineVals.custom_uom_id = customUom;
      }

      const productPrice = product.lst_price || 0;
      const hasCustomPrice =
        customPrice !== undefined &&
        customPrice !== null &&
        Math.abs(productPrice - customPrice) > 0.01;

      if (hasCustomPrice) {
        addLineVals.price_unit = customPrice;
        addLineVals.price_type = "manual";
      }

      const orderLine = await this.pos.addLineToCurrentOrder(
        addLineVals,
        { code },
        product.needToConfigure ? product.needToConfigure() : false
      );
      return orderLine;
    } catch (error) {
      try {
        await this.pos.addLineToCurrentOrder(
          { product_id: product, product_tmpl_id: product.product_tmpl_id },
          { code },
          product.needToConfigure ? product.needToConfigure() : false
        );
      } catch (fallbackError) {
        console.error("Fallback also failed:", fallbackError);
        this.sound?.play("error");
        this.barcodeReader.showNotFoundNotification(code);
      }
    }
  },
});
