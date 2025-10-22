from odoo import models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_invoice(self, move_vals):
        invoice = super()._create_invoice(move_vals)
        if invoice:
            company_code = self.company_id.code or ''
            invoice.is_pos_invoice = True
            # Assign POS-specific sequence if not yet assigned
            if not invoice.name or invoice.name == '/':
                seq = self.env['ir.sequence'].next_by_code('pos.invoice')
                if seq:
                    invoice.name = f"{company_code}/{seq}"
        return invoice