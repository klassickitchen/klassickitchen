# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Ayana KP (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL v3) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models


class AccountMove(models.Model):
    """Inherit the Account Move to add amount in words in account move.
        Methods:_compute_number_to_words(self):
        Function to convert the invoice subtotal amount to words."""
    _inherit = 'account.move'

    number_to_words = fields.Char(string="Amount in Words (Total) : ",
                                  compute='_compute_number_to_words',
                                  help="To showing total amount in words")
    number_to_words_ar = fields.Char(string="Amount in Words (Arabic)", compute='_compute_number_to_words', help="Total amount written in Arabic words")

    def _compute_number_to_words(self):
        """Compute the amount to words in Invoice"""
        for rec in self:
            words = rec.currency_id.amount_to_text(rec.amount_total)
            if rec.currency_id.name == 'QAR':
                import re
                # Replace Rial with Qatari Rials
                words = re.sub(r'\bRials?\b', 'Qatari Riyals', words) #Edited
                # Add "Only" at the end
                if not words.strip().endswith('Only'):
                    words = f"{words.strip()} Only"
            rec.number_to_words = words
            # skip if ar_001 is not installed
            arabic_words = False
            try:
                arabic_words = rec.with_context(lang='ar_001').currency_id.amount_to_text(rec.amount_total)
                if arabic_words and rec.currency_id.name == 'QAR':
                    import re
                    arabic_words = re.sub(r'Rials?|Rial', 'ريال قطري', arabic_words)
            except Exception:
                arabic_words = False

            rec.number_to_words_ar = arabic_words
            print("Amount", rec.number_to_words, rec.number_to_words_ar)
