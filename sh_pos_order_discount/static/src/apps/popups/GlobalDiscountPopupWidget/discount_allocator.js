/** @odoo-module */

import { accountTaxHelpers } from "@account/helpers/account_tax";
import { roundPrecision } from "@web/core/utils/numbers";

export const DEFAULT_DISCOUNT_DIGITS = 2;

/**
 * Quantise a discount percentage to `digits` decimal places (clamped to 0..100).
 */
export function quantizePct(value, digits = DEFAULT_DISCOUNT_DIGITS) {
    const parsed = typeof value === "number" ? value : parseFloat(value);
    if (!Number.isFinite(parsed)) {
        return 0;
    }
    const clamped = Math.min(Math.max(parsed, 0), 100);
    return parseFloat(clamped.toFixed(digits));
}

/**
 * Compute a single POS order line's rounded price-with-tax for a candidate
 * discount percentage, without mutating the line.
 *
 * Uses Odoo's accountTaxHelpers pipeline when available so rounding and tax
 * treatment match PosOrder.taxTotals and account.move.line exactly.
 */
export function computeLinePriceWithTax(line, discountPct, documentSign, company, currency) {
    if (
        typeof line.prepareBaseLineForTaxesComputationExtraValues === "function" &&
        accountTaxHelpers &&
        company
    ) {
        const baseLine = accountTaxHelpers.prepare_base_line_for_taxes_computation(
            line,
            line.prepareBaseLineForTaxesComputationExtraValues({
                quantity: documentSign * line.qty,
                discount: discountPct,
            })
        );
        accountTaxHelpers.add_tax_details_in_base_line(baseLine, company);
        accountTaxHelpers.round_base_lines_tax_details([baseLine], company);
        return documentSign * baseLine.tax_details.total_included_currency;
    }
    const rounding = currency?.rounding || 0.01;
    const raw = documentSign * line.qty * line.price_unit * (1 - discountPct / 100);
    return documentSign * roundPrecision(raw, rounding);
}

/**
 * Pure core allocator working on pre-extracted line evaluators.
 * Separated so both Odoo POS runtime and standalone unit tests use the exact
 * same allocation algorithm.
 *
 * @param {Array<{line: any, signedGrossCents: number, evalSignedAfterCents: (bp: number) => number}>} entries
 * @param {number} targetSignedAfterCents - Desired total (signed by orderSign) in minor units
 * @param {number} discountDigits - Decimal places allowed on each line's discount % (default 2)
 * @returns {{ bps: number[], achievedSignedAfterCents: number }}
 */
export function solveQuantizedAllocation(entries, targetSignedAfterCents, discountDigits = DEFAULT_DISCOUNT_DIGITS) {
    const pctScale = Math.pow(10, discountDigits);
    const maxBp = 100 * pctScale;

    let eligibleGrossCents = 0;
    let nonEligibleSignedCents = 0;
    const eligibleIndices = [];

    for (let i = 0; i < entries.length; i++) {
        if (entries[i].signedGrossCents > 0) {
            eligibleGrossCents += entries[i].signedGrossCents;
            eligibleIndices.push(i);
        } else {
            nonEligibleSignedCents += entries[i].evalSignedAfterCents(0);
        }
    }

    const bps = new Array(entries.length).fill(0);
    if (eligibleIndices.length === 0 || eligibleGrossCents <= 0) {
        return {
            bps,
            achievedSignedAfterCents: nonEligibleSignedCents,
        };
    }

    const desiredEligibleAfterCents = Math.min(
        eligibleGrossCents,
        Math.max(0, targetSignedAfterCents - nonEligibleSignedCents)
    );
    const desiredEligibleDiscCents = eligibleGrossCents - desiredEligibleAfterCents;

    const baseBp = Math.min(
        maxBp,
        Math.max(0, Math.round((desiredEligibleDiscCents / eligibleGrossCents) * maxBp))
    );

    const afterCents = new Array(entries.length).fill(0);
    let currentEligibleAfterCents = 0;
    for (const idx of eligibleIndices) {
        bps[idx] = baseBp;
        afterCents[idx] = entries[idx].evalSignedAfterCents(baseBp);
        currentEligibleAfterCents += afterCents[idx];
    }

    // Coordinate-descent nudges of +/- 1 basis point (0.01%).
    // Every accepted step strictly reduces |err| (a non-negative integer),
    // guaranteeing fast termination with zero risk of cycling.
    const maxIterations = Math.max(500, eligibleIndices.length * 10);
    for (let iter = 0; iter < maxIterations; iter++) {
        const err = currentEligibleAfterCents - desiredEligibleAfterCents;
        if (err === 0) {
            break;
        }
        // err > 0 => total is too high => need MORE discount => increase bp
        // err < 0 => total is too low  => need LESS discount => decrease bp
        const direction = err > 0 ? 1 : -1;
        const absErr = Math.abs(err);

        // Pass 1 keeps all lines within +/- 1 step (0.01%) of baseBp when possible.
        // Pass 2 relaxes the spread limit if needed to close any remaining gap.
        let chosenIdx = -1;
        let chosenNewAfter = 0;

        for (let pass = 0; pass < 2 && chosenIdx === -1; pass++) {
            let bestAbsNewErr = absErr;
            let bestSameSign = false;
            let bestDev = Infinity;
            let bestGross = -1;

            for (const idx of eligibleIndices) {
                const newBp = bps[idx] + direction;
                if (newBp < 0 || newBp > maxBp) {
                    continue;
                }
                const dev = Math.abs(newBp - baseBp);
                if (pass === 0 && dev > 1) {
                    continue;
                }

                const newAfter = entries[idx].evalSignedAfterCents(newBp);
                const delta = newAfter - afterCents[idx];
                if (delta === 0) {
                    continue;
                }

                const newErr = err + delta;
                const absNewErr = Math.abs(newErr);
                if (absNewErr >= absErr) {
                    continue;
                }

                const sameSign = newErr === 0 || (newErr > 0) === (err > 0);
                const gross = entries[idx].signedGrossCents;

                const isBetter =
                    absNewErr < bestAbsNewErr ||
                    (absNewErr === bestAbsNewErr &&
                        (chosenIdx === -1 ||
                            (sameSign && !bestSameSign) ||
                            (sameSign === bestSameSign &&
                                (dev < bestDev || (dev === bestDev && gross > bestGross)))));

                if (isBetter) {
                    bestAbsNewErr = absNewErr;
                    bestSameSign = sameSign;
                    bestDev = dev;
                    bestGross = gross;
                    chosenIdx = idx;
                    chosenNewAfter = newAfter;
                }
            }
        }

        if (chosenIdx === -1) {
            break;
        }

        currentEligibleAfterCents += chosenNewAfter - afterCents[chosenIdx];
        bps[chosenIdx] += direction;
        afterCents[chosenIdx] = chosenNewAfter;
    }

    return {
        bps,
        achievedSignedAfterCents: currentEligibleAfterCents + nonEligibleSignedCents,
    };
}

/**
 * Allocate a Fixed Global Discount across an order's lines using exact
 * `discountDigits`-decimal percentages so POS cart, popup preview, and
 * account.move.line all compute the exact same total.
 *
 * Stacks on top of any discount already present on the order (matching
 * sh_pos_order_discount's existing UX: entering 500 on an order whose
 * current total is 56,024 targets 55,524).
 */
export function allocateFixedGlobalDiscount(
    order,
    inputFixedAmount,
    discountDigits = DEFAULT_DISCOUNT_DIGITS
) {
    const orderlines = order ? order.get_orderlines() : [];
    const currency = order?.config?.currency_id || order?.currency;
    const company = order?.company;
    const currencyDigits = currency?.decimal_places ?? 2;
    const minorScale = Math.pow(10, currencyDigits);
    const pctScale = Math.pow(10, discountDigits);

    const documentSign =
        order?.taxTotals?.order_sign ??
        (orderlines.length === 0 || !orderlines.every((l) => l.qty < 0) ? 1 : -1);

    const currentTotal = order ? order.get_total_with_tax() : 0;
    const addedFixed = Number.isFinite(inputFixedAmount) ? Math.max(0, inputFixedAmount) : 0;

    let grossTotal = 0;
    const lineGrossValues = orderlines.map((line) => {
        const val = computeLinePriceWithTax(line, 0, documentSign, company, currency);
        grossTotal += val;
        return val;
    });

    const orderSign = grossTotal < 0 ? -1 : 1;
    const grossSignedCents = Math.round(orderSign * grossTotal * minorScale);
    const currentSignedCents = Math.round(orderSign * currentTotal * minorScale);
    const addedFixedCents = Math.round(addedFixed * minorScale);
    const targetSignedAfterCents = Math.max(0, currentSignedCents - addedFixedCents);

    const entries = orderlines.map((line, i) => {
        const cache = new Map();
        const signedGrossCents = Math.round(orderSign * lineGrossValues[i] * minorScale);
        cache.set(0, signedGrossCents);
        return {
            line,
            signedGrossCents,
            evalSignedAfterCents(bp) {
                if (cache.has(bp)) {
                    return cache.get(bp);
                }
                const pct = bp / pctScale;
                const price = computeLinePriceWithTax(line, pct, documentSign, company, currency);
                const cents = Math.round(orderSign * price * minorScale);
                cache.set(bp, cents);
                return cents;
            },
        };
    });

    const { bps, achievedSignedAfterCents } = solveQuantizedAllocation(
        entries,
        targetSignedAfterCents,
        discountDigits
    );

    const lineDiscounts = new Map();
    for (let i = 0; i < orderlines.length; i++) {
        lineDiscounts.set(orderlines[i], bps[i] / pctScale);
    }

    const totalAfter = (orderSign * achievedSignedAfterCents) / minorScale;
    const totalDiscount = (grossSignedCents - achievedSignedAfterCents) / minorScale;
    const addedDiscount = (currentSignedCents - achievedSignedAfterCents) / minorScale;
    const effectivePct =
        grossSignedCents > 0
            ? ((grossSignedCents - achievedSignedAfterCents) / grossSignedCents) * 100
            : 0;
    const addedPct =
        currentSignedCents > 0
            ? ((currentSignedCents - achievedSignedAfterCents) / currentSignedCents) * 100
            : 0;

    return {
        lineDiscounts,
        grossTotal,
        currentTotal,
        totalAfter,
        totalDiscount,
        addedDiscount,
        effectivePct,
        addedPct,
    };
}

/**
 * Preview a Percentage Global Discount across an order's lines using exact
 * per-line quantized percentages and currency rounding, matching confirm().
 */
export function previewPercentageGlobalDiscount(
    order,
    inputPct,
    discountDigits = DEFAULT_DISCOUNT_DIGITS
) {
    const orderlines = order ? order.get_orderlines() : [];
    const currency = order?.config?.currency_id || order?.currency;
    const company = order?.company;
    const currencyDigits = currency?.decimal_places ?? 2;
    const minorScale = Math.pow(10, currencyDigits);

    const documentSign =
        order?.taxTotals?.order_sign ??
        (orderlines.length === 0 || !orderlines.every((l) => l.qty < 0) ? 1 : -1);

    const currentTotal = order ? order.get_total_with_tax() : 0;
    const quantizedInputPct = quantizePct(inputPct, discountDigits);

    let totalAfterCents = 0;
    const lineDiscounts = new Map();

    for (const line of orderlines) {
        let newPct;
        if (line.get_discount && line.get_discount()) {
            const currentPrice = line.get_display_price();
            const finalPrice = currentPrice - (currentPrice * quantizedInputPct) / 100;
            const grossLine = line.price_unit * line.qty;
            const compounded = grossLine !== 0 ? ((grossLine - finalPrice) / grossLine) * 100 : 0;
            newPct = quantizePct(compounded, discountDigits);
        } else {
            newPct = quantizedInputPct;
        }
        lineDiscounts.set(line, newPct);
        const afterPrice = computeLinePriceWithTax(line, newPct, documentSign, company, currency);
        totalAfterCents += Math.round(afterPrice * minorScale);
    }

    const totalAfter = totalAfterCents / minorScale;
    const addedDiscount = Math.abs(currentTotal - totalAfter);

    return {
        lineDiscounts,
        totalAfter,
        addedDiscount,
        quantizedPct: quantizedInputPct,
    };
}
