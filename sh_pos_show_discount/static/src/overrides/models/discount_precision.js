/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

/**
 * Decimals a discount percentage is allowed to carry.
 *
 * Must match the 'Discount' decimal precision
 * (Settings -> Technical -> Decimal Accuracy), because that is the precision
 * account.move.line.discount is stored at.
 */
export const DISCOUNT_DIGITS = 2;

/**
 * Quantise a discount percentage to the precision the invoice can store.
 *
 * pos.order.line.discount is declared `digits=0`, which in Odoo means "apply no
 * rounding at all", so POS stores whatever float it is handed. A fixed-amount
 * global discount back-calculates its percentage by division, which almost never
 * lands on two decimals -- e.g. 3264 / 13054 * 100 = 25.003830243603492.
 *
 * account.move.line.discount is declared `digits='Discount'`, so the ORM rounds
 * that value on write and the invoice then recomputes every price_subtotal from
 * the rounded discount. The invoiced total stops matching the amount collected
 * at the till, and cash rounding can widen the difference into a full riyal left
 * behind as "Amount Due".
 *
 * Quantising in POS means both sides work from the same number.
 */
export function quantizeDiscount(value) {
    const parsed = typeof value === "number" ? value : parseFloat(value);
    if (!Number.isFinite(parsed)) {
        // leave NaN / undefined alone; core set_discount already coerces to 0
        return value;
    }
    return parseFloat(parsed.toFixed(DISCOUNT_DIGITS));
}

patch(PosOrderline.prototype, {
    /**
     * Single point where the stored discount is assigned, so quantising here
     * covers every route to it: the global discount popup (fixed and
     * percentage), the per-line discount, and the numpad Disc button.
     */
    set_discount(discount) {
        return super.set_discount(quantizeDiscount(discount));
    },
});
