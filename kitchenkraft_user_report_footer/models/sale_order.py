from odoo import models
from odoo.tools import is_html_empty


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_seller_report_footer(self):
        """Return the salesperson's HTML footer, or False to keep the company footer of the layout."""
        self.ensure_one()
        # sudo: the user printing the quotation may not be allowed to read the salesperson's user record.
        user = self.sudo().user_id or self.sudo().create_uid
        footer = user.report_footer
        return footer if not is_html_empty(footer) else False
