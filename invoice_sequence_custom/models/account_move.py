from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_pos_invoice = fields.Boolean(string="POS Invoice", default=False)
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

    @api.depends('invoice_line_ids')
    def _custom_compute_amount(self):
        for move in self:
            move.amount_discount = sum(
                line.quantity * line.price_unit * (line.discount / 100)
                for line in move.invoice_line_ids
            )

    @api.depends('invoice_line_ids.amount_without_discount')
    def _compute_gross_total(self):
        for move in self:
            gross_total = sum(move.invoice_line_ids.mapped('amount_without_discount'))
            move.gross_total = gross_total

    # @api.depends('invoice_line_ids.sale_line_ids.order_id.payment_type')
    # def _compute_payment_type(self):
    #     for move in self:
    #         if move.is_pos_invoice:
    #             move.payment_type = 'cash'
    #             continue
    #
    #         sale_orders = move.invoice_line_ids.sale_line_ids.mapped('order_id')
    #         if sale_orders:
    #             move.payment_type = sale_orders[0].payment_type
    #         else:
    #             move.payment_type = False
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

            # Only for customer invoices and credit notes
            if move.move_type in ('out_invoice', 'out_refund'):
                if move.name in ('/', False):
                    # Customer Invoice (normal or POS)
                    if move.move_type == 'out_invoice':
                        if move.is_pos_invoice:
                            sequence_code = 'pos.invoice'
                        else:
                            sequence_code = 'account.invoice'
                    # Customer Credit Note
                    elif move.move_type == 'out_refund':
                        sequence_code = 'account.invoice.return'

                    # Get next sequence and assign custom name
                    sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
                    move.name = f"{company_code}/{sequence_number}"

        # Continue with Odoo’s standard post behavior
        res = super().action_post()
        return res

    def action_print_pdf(self):
        self.ensure_one()
        if self.is_pos_invoice:
            invoice_template = self.env.ref('invoice_sequence_custom.dot_matrix_a5')
        else:
            invoice_template = self.env.ref('account.account_invoices_without_payment')
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

