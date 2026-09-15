from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    pos_rounding_absorb = fields.Boolean(
        string="Absorb Small Cash Rounding",
        default=True,
        help="On invoices generated from the Point of Sale, a cash rounding difference no "
             "larger than the threshold below is reported as part of the discount instead "
             "of as a separate Rounding line on the printed invoice.\n"
             "The journal entry is not modified: the difference stays booked on the cash "
             "rounding account.",
    )
    pos_rounding_absorb_threshold = fields.Monetary(
        string="Rounding Absorption Threshold",
        currency_field='currency_id',
        default=0.05,
        help="Largest cash rounding difference that is still considered a side effect of "
             "quantizing a discount, and therefore absorbed into the printed discount.\n"
             "Anything above this is treated as genuine coinage rounding and printed on "
             "its own Rounding line.",
    )
