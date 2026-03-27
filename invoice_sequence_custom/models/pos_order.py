from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_invoice(self, move_vals):
        invoice = super()._create_invoice(move_vals)
        if invoice:
            company_code = self.company_id.code or ''
            invoice.is_pos_invoice = True

            if invoice.move_type == 'out_refund':
                # Find sequence for THIS company specifically
                sequence = self.env['ir.sequence'].search([
                    ('code', '=', 'pos.invoice.return'),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)

                # If not found for this company, create it automatically
                if not sequence:
                    sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'POS Invoice Return',
                        'code': 'pos.invoice.return',
                        'prefix': 'POS RET/',
                        'padding': 4,
                        'company_id': self.company_id.id,
                    })

                seq = sequence.next_by_id()
                if seq:
                    self.env.cr.execute(
                        "UPDATE account_move SET name = %s WHERE id = %s",
                        (f"{company_code}/{seq}", invoice.id)
                    )
                    invoice.invalidate_recordset(['name'])


            elif invoice.move_type == 'out_invoice':
                if not invoice.name or invoice.name == '/':
                    seq = self.env['ir.sequence'].next_by_code('pos.invoice')
                    if seq:
                        invoice.name = f"{company_code}/{seq}"

        return invoice
