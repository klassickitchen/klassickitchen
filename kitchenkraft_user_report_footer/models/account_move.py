from odoo import models
from odoo.tools import is_html_empty


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_seller_user(self):
        """Find the salesperson/cashier who sold the invoice."""
        self.ensure_one()
        # sudo: the user printing the invoice may not have POS or Sales access.
        move = self.sudo()
        # 1. From Invoice Salesperson (POS sets it to the POS order user)
        if move.invoice_user_id:
            return move.invoice_user_id
        # 2. From POS Order (for POS invoices)
        pos_user = move.pos_order_ids[:1].user_id
        if pos_user:
            return pos_user
        # 3. From Sale Order
        sale_user = move.invoice_line_ids.sale_line_ids.order_id[:1].user_id
        if sale_user:
            return sale_user
        # 4. Fallback to creator
        return move.create_uid

    def _get_seller_report_footer(self):
        """Return the seller's HTML footer, or False to keep the company footer of the layout."""
        self.ensure_one()
        footer = self._get_seller_user().report_footer
        return footer if not is_html_empty(footer) else False
