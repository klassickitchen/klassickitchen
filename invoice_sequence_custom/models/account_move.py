from odoo import models, api, fields
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_pos_invoice = fields.Boolean(string="POS Invoice", default=False)
    cash_rounding_amount = fields.Monetary(
        string="Cash Rounding",
        currency_field='currency_id',
        compute='_compute_cash_rounding_amount',
        help="Signed cash rounding difference carried by this invoice, in invoice currency. "
             "This is the figure the Rounding line prints.",
    )
    pos_rounding_absorbed = fields.Boolean(
        string="Rounding Absorbed In Discount",
        copy=False,
        help="Set once, on the draft POS invoice, when the cash rounding difference was small "
             "enough to be reported as part of the discount. Frozen at that point so that a "
             "later change to the company threshold never reprints an existing invoice "
             "differently.",
    )
    payment_type = fields.Selection(
        [('cash', 'Cash'),
         ('credit', 'Credit')],
        string='Cash|Credit',
        compute="_compute_payment_type"
    )
    gross_total = fields.Monetary(
        store=True,
        string="Gross Total",
        compute="_compute_gross_total",
    )

    amount_discount = fields.Monetary(
        string="Total Discount", currency_field='currency_id', compute='_custom_compute_amount'
    )

    description_display = fields.Selection([
        ('product_name', 'Product Name'),
        ('remove_description', 'Remove Description'),
        ('show_description_only', 'Show Description Only'),
    ], string='Description Display', default='remove_description')

    @api.depends('invoice_line_ids.price_subtotal',
                 'invoice_line_ids.amount_without_discount',
                 'cash_rounding_amount', 'pos_rounding_absorbed')
    def _custom_compute_amount(self):
        # Print Gross - Untaxed, never a separately rounded sum.
        #
        # price_subtotal is rounded to the currency once per line, whereas
        # summing quantity * price_unit * discount/100 rounds only at the end.
        # The two do not agree: on KK/POS/0088 the exact discount is 57.998,
        # which prints as 58.00, while the lines total 130.01 -- so the block
        # read 188.00 - 58.00 = 130.01 and did not add up. Deriving the discount
        # from the two figures that are actually printed makes it reconcile by
        # construction, for any discount percentage.
        for move in self:
            product_lines = move.invoice_line_ids.filtered(
                lambda line: line.display_type == 'product'
            )
            net_total = sum(product_lines.mapped('price_subtotal'))
            if move.pos_rounding_absorbed:
                # The rounding is no longer printed on a line of its own, so it has to land
                # somewhere or the block stops adding up. Netting it off here makes the
                # printed discount the difference between the two other printed figures:
                # Gross Total - Net Total, which is what the customer was actually given.
                net_total += move.cash_rounding_amount
            move.amount_discount = move.gross_total - net_total

    @api.depends('invoice_line_ids.amount_without_discount')
    def _compute_gross_total(self):
        for move in self:
            gross_total = sum(move.invoice_line_ids.mapped('amount_without_discount'))
            move.gross_total = gross_total

    @api.depends('line_ids.display_type', 'line_ids.amount_currency', 'move_type')
    def _compute_cash_rounding_amount(self):
        # direction_sign * amount_currency is the same expression core uses in
        # _prepare_cash_rounding_base_line_for_taxes_computation, so this always equals the
        # 'cash_rounding_base_amount_currency' that the Rounding row renders.
        for move in self:
            rounding_lines = move.line_ids.filtered(
                lambda line: line.display_type == 'rounding'
            )
            move.cash_rounding_amount = move.direction_sign * sum(
                rounding_lines.mapped('amount_currency')
            )

    def _absorb_cash_rounding_in_discount(self):
        """Freeze the absorb/keep decision on a draft invoice, before it is posted.

        Nothing is written to the journal entry: the rounding line stays exactly where Odoo
        booked it. Only the way the invoice reports itself changes.
        """
        for move in self:
            company = move.company_id
            absorbed = False
            if company.pos_rounding_absorb and not move.currency_id.is_zero(move.cash_rounding_amount):
                threshold = company.pos_rounding_absorb_threshold
                absorbed = threshold > 0.0 and float_compare(
                    abs(move.cash_rounding_amount),
                    threshold,
                    precision_rounding=move.currency_id.rounding,
                ) <= 0
            move.pos_rounding_absorbed = absorbed

    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for move in self:
            totals = move.tax_totals
            if not move.pos_rounding_absorbed or not totals:
                continue
            # Fold the rounding back into the untaxed base and drop the key the totals
            # template keys the Rounding row off. The total is unchanged -- core builds it as
            # base + tax + rounding, and the rounding it subtracted from the base is exactly
            # what we add back -- so the invoice still totals what the customer paid.
            delta_currency = totals.pop('cash_rounding_base_amount_currency', 0.0)
            delta = totals.pop('cash_rounding_base_amount', 0.0)
            if not delta_currency and not delta:
                continue
            totals['base_amount_currency'] += delta_currency
            totals['base_amount'] += delta
            for subtotal in totals.get('subtotals', []):
                subtotal['base_amount_currency'] += delta_currency
                subtotal['base_amount'] += delta
            move.tax_totals = totals

    @api.depends('invoice_line_ids.sale_line_ids.order_id.payment_type')
    def _compute_payment_type(self):
        for move in self:
            if move.is_pos_invoice:
                move.payment_type = 'cash'
                continue

            sale_orders = move.invoice_line_ids.sale_line_ids.mapped('order_id')
            if sale_orders:
                move.payment_type = sale_orders[0].payment_type
            else:
                move.payment_type = False

    # @api.model
    # def create(self, vals_list):
    #     print('createeeeeeee')
    #     res = super(AccountMove, self).create(vals_list)
    #     if self.env.context.get('linked_to_pos'):
    #         print(self.env.context.get('linked_to_pos'), 'contextttttttt')
    #         for move in res:
    #             move.payment_type = 'cash'
    #         print("payment type", move.payment_type)
    #         print(res, 'resssssssssss')
    #     return res

    def action_post(self):
        for move in self:
            company_code = move.company_id.code or ''

            if move.move_type in ('out_invoice', 'out_refund'):
                needs_sequence = (
                        move.name in ('/', False)
                        or (move.move_type == 'out_refund' and move.name.startswith('RINV/'))
                )

                if needs_sequence:
                    if move.move_type == 'out_invoice':
                        if move.is_pos_invoice:
                            sequence_code = 'pos.invoice'
                        else:
                            sequence_code = 'account.invoice'
                    elif move.move_type == 'out_refund':
                        sequence_code = 'account.invoice.return'

                    sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
                    if sequence_number:
                        self.env.cr.execute(
                            "UPDATE account_move SET name = %s WHERE id = %s",
                            (f"{company_code}/{sequence_number}", move.id)
                        )
                        move.invalidate_recordset(['name'])

        res = super().action_post()
        return res

    def action_print_pdf(self):
        self.ensure_one()
        if self.is_pos_invoice:
            invoice_template = self.env.ref('invoice_sequence_custom.action_print_pdf_a5')
        else:
            invoice_template = self.env.ref('invoice_sequence_custom.account_invoices_a4')
        report_action = invoice_template.report_action(self.id, config=False)
        return self._get_action_with_base_document_layout_configurator(report_action)

    # def action_print_pdf_with_header_footer(self):
    #     self.ensure_one()
    #     ctx = dict(self.env.context)
    #     ctx['include_header_footer'] = True
    #
    #     if self.is_pos_invoice:
    #         invoice_template = self.env.ref('invoice_sequence_custom.account_invoices_a5')
    #     else:
    #         invoice_template = self.env.ref('invoice_sequence_custom.account_invoices_a4')
    #
    #     report_action = invoice_template.report_action(self.id, config=False)
    #     report_action['context'] = ctx
    #     return self._get_action_with_base_document_layout_configurator

    # def _prepare_product_base_line_for_taxes_computation(self, product_line):
    #     """Override to remove discount logic completely during tax computation."""
    #     self.ensure_one()
    #     is_invoice = self.is_invoice(include_receipts=True)
    #     sign = self.direction_sign if is_invoice else 1
    #
    #     if is_invoice:
    #         rate = self.invoice_currency_rate
    #     else:
    #         rate = (abs(product_line.amount_currency) / abs(product_line.balance)) if product_line.balance else 0.0
    #
    #     return self.env['account.tax']._prepare_base_line_for_taxes_computation(
    #         product_line,
    #         price_unit=product_line.price_unit if is_invoice else product_line.amount_currency,
    #         quantity=product_line.quantity if is_invoice else 1.0,
    #         discount=0.0,
    #         rate=rate,
    #         sign=sign,
    #         special_mode=False if is_invoice else 'total_excluded',
    #     )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    amount_without_discount = fields.Monetary(
        string="Amount",
        compute="_compute_amount_without_discount",
        store=True,
    )

    @api.depends('quantity', 'price_unit', 'currency_id')
    def _compute_amount_without_discount(self):
        for line in self:
            if line.display_type not in ('product', 'cogs'):
                line.amount_without_discount = 0.0
                continue

            line.amount_without_discount = line.price_unit * line.quantity

    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    # def _compute_totals(self):
    #     super()._compute_totals()
    #     for line in self:
    #         if line.display_type not in ('product', 'cogs'):
    #             continue
    #
    #         line.price_subtotal = line.price_unit * line.quantity
