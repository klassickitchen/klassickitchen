# Sale Price on the Delivery Slip

How `stock.move.product_sale_price` is calculated, and exactly what prints on the
Delivery Slip in every scenario — including multiple barcodes on one product.

---

## 1. Is the customization complete?

**Yes for the reporting layer.** The field now reads the real transaction price instead
of the product master price, and the Sale Price column prints on the Delivery Slip.

**With one inherent limitation** that cannot be fixed in the report: when the *same
product* is sold under *two different barcodes* in the *same order*, POS creates only
**one** stock move for both. There is no second row to put the second price on. See
[Scenario D](#scenario-d--two-barcodes-same-product-same-order-same-uom).

### Files changed

| File | Change |
|---|---|
| `kitchenkraft_quotation_custom/models/stock_move.py` | `product_sale_price` is now computed, not `related` |
| `kitchenkraft_quotation_custom/__manifest__.py` | `+ sale_stock` dependency, version → `18.0.1.4` |
| `bi_order_line_with_sequence_number/report/order_line_inherit_report.xml` | Sale Price column added to both delivery tables |
| `bi_order_line_with_sequence_number/__manifest__.py` | `+ kitchenkraft_quotation_custom` dependency, version → `18.0.0.5` |

Applied identically to `kitchen_craft/staging/klassickitchen/` and
`kitchen_craft/klassickitchen/`.

### To make it appear

```bash
odoo-bin -u kitchenkraft_quotation_custom,bi_order_line_with_sequence_number -d <db>
```

Both modules must be upgraded. The report module now depends on the quotation module,
so the field is guaranteed to exist before the report renders.

> **Note:** the Sale Price column has **no group restriction** — unlike the `No.` column,
> which is limited to `bi_order_line_with_sequence_number.access_display_order_line_number`.
> Anyone who prints a Delivery Slip sees the price, including the copy handed to the
> customer. Tell me if that column should be restricted to a group.

---

## 2. Where the price actually comes from

The barcode price reaches the stock move indirectly, through the order line:

```
product.barcode.price
   ↓  pos_session.py  find_product_by_barcode()   (searches barcode + company)
   ↓  overrides lst_price, attaches _barcode_price / _barcode_uom_id
   ↓  product_screen.js  _addProductWithCustomBarcode()
   ↓  sets price_unit + price_type = "manual"  (blocks pricelist recomputation)
pos.order.line.price_unit          ← the price actually charged, stored in the DB
   ↓  stock.picking.pos_order_id
stock.move.product_sale_price      ← what prints on the slip
```

### Important: the barcode itself is not recorded

`pos.order.line` has **no barcode field** — neither in Odoo core nor in
`kitchenkraft_multiple_barcode`. Once the sale is saved, only the **price** and the
**UoM** survive; which barcode was scanned is lost.

This is why the slip can show *the price that was charged*, but can never show
*which barcode produced it*.

---

## 3. Decision logic

`_compute_product_sale_price` resolves in this order, first match wins:

| # | Condition | Value used |
|---|---|---|
| 1 | Move linked to a Sale Order (`sale_line_id`) | `sale_line_id.price_unit` |
| 2 | Move's picking linked to a POS order, all matching lines same price | that price |
| 3 | Move's picking linked to a POS order, prices differ | **quantity-weighted average** |
| 4 | No order behind the move | `product_id.list_price` (product master) |

POS lookup uses `picking_id.pos_order_id`, falling back to `group_id.pos_order_id`
for the POS "ship later" flow. Both reads are `sudo()` — inventory users have read
access to neither `pos.order.line` nor `sale.order.line`, so without it the slip
would raise an AccessError for warehouse staff.

---

## 4. Scenarios

All scenarios use this product:

**Cabinet Handle CH-200** — product master Sales Price (`list_price`) = **12.00**

| Barcode | UoM | `product.barcode.price` |
|---|---|---|
| `8901234500011` | Units | 10.00 |
| `8901234500028` | Units | 25.00 |
| `8901234500035` | Box | 100.00 |

---

### Scenario A — Sale Order delivery

**Sale Order S00123**

| Line | Product | Qty | Unit Price |
|---|---|---|---|
| 1 | CH-200 | 4 | 12.00 |

Delivery `WH/OUT/00045`, one stock move, `sale_line_id` set → **rule 1**.

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 4.00 Units | **12.00** |

✅ Exact.

---

### Scenario B — POS, one barcode

**POS Order POS/0041** — scanned `8901234500011` three times.

The three scans merge into one order line (same price, same UoM):

| Line | Product | Qty | `price_unit` |
|---|---|---|---|
| 1 | CH-200 | 3 | 10.00 |

One stock move, qty 3. All matching lines share one price → **rule 2**.

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 3.00 Units | **10.00** |

✅ Exact — the barcode price, not the 12.00 product master price. **This is the case
the customization was built for.**

---

### Scenario C — POS, one barcode, price manually overridden by the cashier

**POS Order POS/0042** — scanned `8901234500011` (10.00), cashier changed it to 9.50.

| Line | Product | Qty | `price_unit` |
|---|---|---|---|
| 1 | CH-200 | 2 | 9.50 |

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 2.00 Units | **9.50** |

✅ Exact. The slip follows what was actually charged, not the barcode's configured price.

---

### Scenario D — Two barcodes, same product, same order, same UoM

**⚠️ This is your question.**

**POS Order POS/0043**

| Line | Scanned | Product | Qty | `price_unit` |
|---|---|---|---|---|
| 1 | `8901234500011` | CH-200 | 2 | 10.00 |
| 2 | `8901234500028` | CH-200 | 1 | 25.00 |

The two lines correctly stay **separate** in POS — `can_be_merged_with` refuses to
merge lines whose prices differ by more than 0.01.

But on validation, `_create_move_from_pos_order_lines` groups order lines by
`product_id` **only**:

```python
lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id),
                           key=lambda l: l.product_id.id)
```

→ **2 order lines collapse into 1 stock move**, qty = 2 + 1 = 3.

There is no second move, so there can be no second slip row. **Rule 3** applies:

```
(10.00 × 2) + (25.00 × 1)     20.00 + 25.00     45.00
─────────────────────────  =  ─────────────  =  ─────  =  15.00
         2 + 1                       3            3
```

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 3.00 Units | **15.00** |

⚠️ **Neither 10.00 nor 25.00.** The weighted average was chosen because it is the only
value where `Sale Price × Delivered` still reconciles to what the customer actually
paid: `15.00 × 3 = 45.00` ✅.

A simple average would give `17.50 × 3 = 52.50` ✗, and picking the first line's price
would give `10.00 × 3 = 30.00` ✗.

---

### Scenario E — Two barcodes, same product, same order, **different UoM**

**⚠️ Pre-existing defect — both numbers are wrong, and it is not caused by this change.**

**POS Order POS/0044**

| Line | Scanned | Product | Qty | UoM | `price_unit` |
|---|---|---|---|---|---|
| 1 | `8901234500011` | CH-200 | 2 | Units | 10.00 |
| 2 | `8901234500035` | CH-200 | 1 | Box (12 Units) | 100.00 |

`_prepare_stock_move_vals` takes the UoM from the **first** line but sums **raw
quantities** across both:

```python
'product_uom':    first_line.product_uom_id.id,              # Units
'product_uom_qty': abs(sum(order_lines.mapped('qty'))),      # 2 + 1 = 3
```

→ one move of **3 Units**. The true delivered amount is `2 + (1 × 12) = 14 Units`.

The weighted average then inherits that broken quantity:

```
(10.00 × 2) + (100.00 × 1)     120.00
──────────────────────────  =  ──────  =  40.00
          2 + 1                   3
```

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 3.00 Units | **40.00** |

❌ Quantity wrong (3 instead of 14), price meaningless.

**Root cause:** the quantity bug in `kitchenkraft_multiple_barcode/models/stock_picking.py`,
which mixes UoMs without conversion. It existed before this change and affects stock
levels and valuation, not just the report. Fixing it is a separate job — see
[section 6](#6-if-you-need-one-row-per-barcode).

---

### Scenario F — POS refund

**POS Order POS/0045** — refund of one CH-200 sold at 25.00.

| Line | Product | Qty | `price_unit` |
|---|---|---|---|
| 1 | CH-200 | −1 | 25.00 |

A return picking is created. The compute uses `abs()` on quantities, so signs do not
distort the result. Single price → **rule 2**.

**Delivery Slip:**

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 1.00 Units | **25.00** |

✅ Exact.

---

### Scenario G — Internal transfer (no order behind it)

**Transfer `WH/INT/00012`** — 5 × CH-200 moved between locations. No `sale_line_id`,
no `pos_order_id` → **rule 4**.

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 5.00 Units | **12.00** ← product master |

✅ Correct behaviour — unchanged from before. This is also what the Sale Price column
shows in the **picking form view**, which is restricted to internal transfers
(`column_invisible="parent.picking_type_code != 'internal'"`).

---

### Scenario H — Product on the picking but not on the order

Happens with phantom-BoM components: POS explodes a kit, so the move's product never
appears on any POS order line. `lines` comes back empty → **rule 4**, product master
price. Same output shape as Scenario G.

---

### Scenario I — Sale Order with a discount ⚠️

**Sale Order S00124**

| Line | Product | Qty | Unit Price | Discount |
|---|---|---|---|---|
| 1 | CH-200 | 4 | 12.00 | 10% |

`sale_line_id.price_unit` is the price **before** discount.

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 4.00 Units | **12.00** ← not 10.80 |

⚠️ By design, matching the agreed plan. For barcode pricing this is correct — the
barcode price *is* `price_unit`. If the slip should instead show the net price, the
compute needs `price_unit * (1 - discount / 100)`. Tell me and I'll change it.

---

## 5. Summary table

| Scenario | Slip shows | Correct? |
|---|---|---|
| A — Sale Order | SO line unit price | ✅ |
| B — POS, one barcode | that barcode's price | ✅ |
| C — POS, cashier override | the overridden price | ✅ |
| D — 2 barcodes, same UoM | weighted average | ⚠️ blended, reconciles to total |
| E — 2 barcodes, different UoM | weighted avg over a wrong qty | ❌ pre-existing defect |
| F — POS refund | the refunded price | ✅ |
| G — Internal transfer | product master price | ✅ by design |
| H — Product not on order | product master price | ✅ by design |
| I — SO with discount | pre-discount price | ⚠️ by design |

---

## 6. If you need one row per barcode

Scenarios D and E both trace back to the same root cause: **POS groups stock moves by
product only**. Fixing that solves the blended price *and* the wrong quantity together.

Override `_create_move_from_pos_order_lines` in `kitchenkraft_multiple_barcode` to group
by `(product_id, product_uom_id, price_unit)` instead of `product_id` alone. Scenario D
would then produce:

| No. | Product | Delivered | Sale Price |
|---|---|---|---|
| 1 | Cabinet Handle CH-200 | 2.00 Units | 10.00 |
| 2 | Cabinet Handle CH-200 | 1.00 Units | 25.00 |

**This is not a report change.** It alters which stock moves get created, so it touches
inventory records, stock valuation and accounting entries. It needs its own testing
round and should not be bundled with this one.

**Decide it on real usage:** if cashiers rarely ring the same product under two
barcodes in one transaction, the weighted average is acceptable edge-case behaviour.
If it is routine, the slip will mislead and the grouping fix is the real answer.

---

## 7. Testing checklist

- [ ] Upgrade both modules, restart, hard-refresh the browser (POS assets)
- [ ] **Scenario B** — POS sale, one barcode → slip shows the barcode price, not 12.00
- [ ] **Scenario A** — SO delivery → slip shows the SO unit price
- [ ] **Scenario D** — two barcodes, one order → confirm the blended value is acceptable
- [ ] **Scenario G** — internal transfer → still shows the product master price
- [ ] Print a slip as a **stock-user-only** account (no POS, no Sales rights) → must not
      raise AccessError. This is what the `sudo()` calls protect.
- [ ] Confirm the price column is acceptable on the customer's copy of the slip

### One thing worth checking separately

`find_product_by_barcode` overwrites `lst_price` on the product record it sends to the
POS frontend. I have not traced whether that value persists in the browser's in-memory
product cache for the rest of the session. If it does, scanning a barcode could change
the price shown when someone later **clicks** that same product from the product grid.

To check: scan `8901234500011` (10.00), then click CH-200 in the product grid and see
whether it prices at 12.00 (correct) or 10.00 (cache polluted). Unrelated to this
change, but easy to test at the same time.
