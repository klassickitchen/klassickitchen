from odoo import models, fields, api, _
from deep_translator import GoogleTranslator
import logging


_logger = logging.getLogger(__name__)



class ProductProduct(models.Model):
    _inherit = "product.product"

    alternative_barcode_ids = fields.One2many(
        "product.barcode",
        "product_id",
        string="Alternative Barcodes",
    )
    arabic_price_alt = fields.Char(
        string='Arabic Price Alt',
        compute='_compute_arabic_price_alt',
        store=True
    )

    @api.depends('alternative_barcode_ids.arabic_price_alt')
    def _compute_arabic_price_alt(self):
        for product in self:
            if product.alternative_barcode_ids:
                product.arabic_price_alt = product.alternative_barcode_ids.arabic_price_alt
            else:
                product.arabic_price_alt = 0.0


    arabic_name = fields.Char(string='Arabic Name')
    translation_error = fields.Boolean(string='Translation Error')

    def _translate_to_arabic(self, text):
        """Helper method to handle translation with proper error handling."""
        if not text:
            return False

        try:
            translator = GoogleTranslator(source='auto', target='ar')
            translated = translator.translate(text)

            # Check if translation actually returned Arabic text
            if translated and any('\u0600' <= c <= '\u06FF' for c in translated):
                return translated
            return False

        except Exception as e:
            _logger.error("Translation error for product %s: %s", self.name, str(e))
            return False

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                translated = record._translate_to_arabic(record.name)
                record.arabic_name = translated
                record.translation_error = not bool(translated)
            else:
                record.arabic_name = False
                record.translation_error = False

    def action_retry_translation(self):
        """Action to manually retry failed translations."""
        for record in self:
            if record.name:
                translated = record._translate_to_arabic(record.name)
                record.write({
                    'arabic_name': translated,
                    'translation_error': not bool(translated)
                })
        return True

    ENGLISH_CHARS = "0123456789."
    ARABIC_CHARS = "٠١٢٣٤٥٦٧٨٩٫"

    # Define the translation table once as a class attribute
    ARABIC_NUMERALS = str.maketrans(ENGLISH_CHARS, ARABIC_CHARS)

    arabic_price = fields.Char(
        string="Arabic Price",
        compute="_compute_arabic_price",
        store=True
    )

    @api.depends('lst_price')  # <-- Crucial decorator must be present!
    def _compute_arabic_price(self):
        # Access the class attribute
        translation_table = self.ARABIC_NUMERALS

        for rec in self:
            if rec.lst_price is not None:
                # 1. Format the float to a string with 2 decimal places
                formatted = "{:.2f}".format(rec.lst_price)

                # 2. Translate the entire formatted string in one go
                rec.arabic_price = formatted.translate(translation_table)
            else:
                rec.arabic_price = False  # Use False or ""



