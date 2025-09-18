from odoo import models, fields, api
from deep_translator import GoogleTranslator
import logging

_logger = logging.getLogger(__name__)


class ProductArabic(models.Model):
    _inherit = "product.template"

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