from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_pos_invoice = fields.Boolean(string="POS Invoice", default=False)
    # payment_type = fields.Selection(
    #     [('cash', 'Cash'),
    #      ('credit', 'Credit')],
    #     string='Cash|Credit',
    #     compute="_compute_payment_type"
    # )
    #
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
            invoice_template = self.env.ref('invoice_sequence_custom.account_invoices_a5')
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
    #     return self._get_action_with_base_document_layout_configurator(report_action)

