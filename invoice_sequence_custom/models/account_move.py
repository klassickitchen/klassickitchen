from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_pos_invoice = fields.Boolean(string="POS Invoice", default=False)

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
