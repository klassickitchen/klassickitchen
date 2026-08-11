from odoo import models, fields, api, _
from odoo.osv import expression
from deep_translator import GoogleTranslator
import logging


_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    brand = fields.Char(string="Brand")
    country_of_origin = fields.Many2one("res.country", string="Country of Origin")

    alternative_barcode_ids = fields.One2many(
        "product.barcode",
        "product_id",
        string="Alternative Barcodes",
    )
    catalogue_hidden_company_ids = fields.Many2many(
        "res.company",
        "product_product_hidden_company_rel",
        "product_id",
        "company_id",
        string="Hidden From Companies",
        compute="_compute_catalogue_hidden_company_ids",
        store=True,
        help="Companies that must not use this product: those managing their catalogue "
             "by barcode that have no barcode row for it. Empty when no such company "
             "claims the product, so barcode-less items stay available everywhere.",
    )

    @api.depends("alternative_barcode_ids.company_id")
    def _compute_catalogue_hidden_company_ids(self):
        """Companies the product must be hidden from, by barcode ownership.

        A company "manages its catalogue by barcode" when it owns at least one
        product.barcode row. That is read from the data rather than configured, so a
        company that never sold over the counter (Al-Saif, Al Diyafa) never lands in
        the hidden set and is therefore never filtered.
        """
        groups = self.env["product.barcode"].sudo()._read_group(
            [("company_id", "!=", False)], ["company_id"]
        )
        separated = self.env["res.company"].browse([group[0].id for group in groups])
        for product in self:
            # sudo: product.barcode carries its own company record rule, so a Kitchen
            # Kraft user reads none of the Klassic rows; without sudo a recompute
            # triggered from one company would store a wrong set for the other.
            owners = product.sudo().alternative_barcode_ids.company_id
            product.catalogue_hidden_company_ids = (separated - owners) if owners else False

    arabic_price_alt = fields.Char(
        string="Arabic Price Alt", compute="_compute_arabic_price_alt", store=True
    )
    product_price = fields.Float(
        string="Computed Price",
        compute="_compute_price_for_company",
    )

    def _load_pos_data_fields(self, config_id):
        """Extend to include qty_available and virtual_available in POS data fields."""
        fields = super(ProductProduct, self)._load_pos_data_fields(config_id)
        if "product_price" not in fields:
            fields.append("product_price")

        return fields

    @api.depends(
        "alternative_barcode_ids.uom_id",
        "alternative_barcode_ids.price",
        "alternative_barcode_ids.company_id",
    )
    # def _compute_price_for_company(self):
    #     print("testing")
    #     current_company = self.env.company
    #     for rec in self:
    #         # Filter barcodes belonging to current company only
    #         product_barcodes = rec.alternative_barcode_ids.filtered(
    #             lambda b: b.company_id == current_company
    #         )

    #         # Try to find barcode matching product's own UoM
    #         barcode_record = product_barcodes.filtered(
    #             lambda b: b.uom_id == rec.uom_id
    #         )[:1]
    #         print(barcode_record, "lo0zzzz")

    #         # If not found, fallback to single barcode (if exactly one exists)
    #         if not barcode_record and len(product_barcodes) == 1:
    #             print("ifffzzzzzz")
    #             barcode_record = product_barcodes[0]

    #         # Assign computed price
    #         if barcode_record:
    #             rec.product_price = barcode_record.price
    #         else:
    #             rec.product_price = rec.lst_price

    # The following method optimizes product price computation by replacing inefficient per-product 
    # ORM queries with a single, batch-processed SQL query. This significantly improves performance 
    # when handling large numbers of products by resolving the "N+1" query bottleneck.
    def _compute_price_for_company(self):
        """Compute product_price using a single SQL query instead of per-product ORM calls."""
        if not self.ids:
            for rec in self:
                rec.product_price = rec.lst_price
            return

        current_company_id = self.env.company.id

        # ONE SQL query for ALL products at once
        # Note: uom_id is on product_template, not product_product
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (pb.product_id)
                pb.product_id,
                pb.price
            FROM product_barcode pb
            JOIN product_product pp ON pp.id = pb.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE pb.product_id IN %s
            AND pb.company_id = %s
            ORDER BY pb.product_id,
                CASE WHEN pb.uom_id = pt.uom_id THEN 0 ELSE 1 END,
                pb.id
        """,
            (tuple(self.ids), current_company_id),
        )

        price_map = dict(self.env.cr.fetchall())

        for rec in self:
            rec.product_price = price_map.get(rec.id, rec.lst_price)

    # By using a single SQL DISTINCT ON query, the system retrieves only the most relevant price 
    # record for each product, prioritizing those that match the product's primary Unit of Measure. 
    # This results in a drastic reduction in database calls and overall server response time.

    @api.depends("alternative_barcode_ids.arabic_price_alt")
    def _compute_arabic_price_alt(self):
        for product in self:
            if product.alternative_barcode_ids:
                product.arabic_price_alt = product.alternative_barcode_ids[
                    0
                ].arabic_price_alt
            else:
                product.arabic_price_alt = 0.0

    arabic_name = fields.Char(string="Arabic Name")
    translation_error = fields.Boolean(string="Translation Error")

    def _translate_to_arabic(self, text):
        """Helper method to handle translation with proper error handling."""
        if not text:
            return False

        try:
            translator = GoogleTranslator(source="auto", target="ar")
            translated = translator.translate(text)

            # Check if translation actually returned Arabic text
            if translated and any("\u0600" <= c <= "\u06ff" for c in translated):
                return translated
            return False

        except Exception as e:
            _logger.error("Translation error for product %s: %s", self.name, str(e))
            return False

    @api.onchange("name")
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
                record.write(
                    {
                        "arabic_name": translated,
                        "translation_error": not bool(translated),
                    }
                )
        return True

    ENGLISH_CHARS = "0123456789."
    ARABIC_CHARS = "٠١٢٣٤٥٦٧٨٩٫"

    # Define the translation table once as a class attribute
    ARABIC_NUMERALS = str.maketrans(ENGLISH_CHARS, ARABIC_CHARS)

    arabic_price = fields.Char(
        string="Arabic Price", compute="_compute_arabic_price", store=True
    )

    @api.depends("lst_price")  # <-- Crucial decorator must be present!
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

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Extend name_search to also look up barcodes from product.barcode model."""
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if not res and name:
            # Search in the custom product.barcode model with company filter
            current_company = self.env.company.id
            barcode_records = self.env["product.barcode"].search(
                [
                    ("barcode", "=", name),
                    ("company_id", "=", current_company),
                ]
            )
            if barcode_records:
                products = barcode_records.mapped("product_id")
                domain = args or []
                if domain:
                    products = products.filtered_domain(domain)
                res = [(p.id, p.display_name) for p in products[:limit]]
        return res

    @api.model
    def _search_display_name(self, operator, value):
        """Extend display_name search to also check product.barcode model."""
        domain = super()._search_display_name(operator, value)
        is_positive = operator not in expression.NEGATIVE_TERM_OPERATORS
        if operator in ("=", "in") or (operator.endswith("like") and is_positive):
            barcode_values = [value] if operator != "in" else value
            current_company = self.env.company.id
            # Find product IDs from product.barcode with company filter
            barcode_records = self.env["product.barcode"].search(
                [
                    ("barcode", "in", barcode_values),
                    ("company_id", "=", current_company),
                ]
            )
            if barcode_records:
                product_ids = barcode_records.mapped("product_id").ids
                barcode_domain = [("id", "in", product_ids)]
            else:
                barcode_domain = [
                    ("alternative_barcode_ids.barcode", "in", barcode_values)
                ]
            domain = expression.OR([domain, barcode_domain])
        return domain
