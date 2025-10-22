from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_pos_invoice = fields.Boolean(string="POS Invoice", default=False)

    def action_post(self):
        for move in self:
            company_code = move.company_id.code or ''

            if move.is_pos_invoice:
                if move.name in ('/', False):
                    sequence_number = self.env['ir.sequence'].next_by_code('pos.invoice')
                    move.name = f"{company_code}/{sequence_number}"
            else:
                if move.name in ('/', False):
                    sequence_number = self.env['ir.sequence'].next_by_code('account.invoice')
                    move.name = f"{company_code}/{sequence_number}"

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
