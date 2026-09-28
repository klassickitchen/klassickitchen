from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # prefetch=False: res.users is read on every request, and this HTML may hold a banner image.
    report_footer = fields.Html(
        string="Report Footer",
        sanitize=False,
        prefetch=False,
        help="Custom HTML or image footer printed on 'Print PDF' invoices sold by this user / showroom. "
             "Leave empty to use the company footer.",
    )
