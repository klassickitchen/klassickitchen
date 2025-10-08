from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductBarcode(models.Model):
    _name = "product.barcode"
    _description = "Product Barcode"
    _inherit = ["pos.load.mixin"]

    product_id = fields.Many2one(
        "product.product", string="Product", ondelete="cascade", required=True
    )
    barcode = fields.Char(string="Barcode", required=True)
    # --- Modified uom_id field ---
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        required=True,
        # Add a dynamic domain based on the product_id's UoM category
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    # --- Helper computed field for the domain ---
    # This field isn't strictly necessary to store, but makes the domain cleaner
    # Alternatively, you could put the logic directly in the domain string,
    # but that can become less readable.
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id",
        string="Product UOM Category",
        readonly=True,
        store=False,  # No need to store this helper field
    )
    price = fields.Float(string="Price", required=True)
    arabic_price_alt=fields.Char(string="Arabic Price ",compute='_compute_arabic_price_alt', store=True)

    _sql_constraints = [
        (
            "barcode_unique",
            "unique(barcode, product_id)",
            "Barcode must be unique per product!",
        ),
    ]

    @api.model
    def default_get(self, fields_list):  # Renamed 'fields' to 'fields_list' for clarity
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        if active_model == "product.product":
            active_id = self.env.context.get("active_id")
            if active_id:
                # Also set the default category if product is set
                product = self.env["product.product"].browse(active_id)
                if product.exists() and "product_id" in fields_list:
                    res["product_id"] = active_id
                # Note: The domain will filter based on the selected product,
                # setting a default uom_id might require more complex logic
                # if you want it pre-filled based on the product.
        return res

    @api.constrains("price")
    def _check_price_not_negative(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("Price cannot be negative."))

    @api.constrains("barcode")
    def _check_barcode_is_unique(self):
        # Consider renaming this to _check_barcode_is_globally_unique for clarity
        # if the intent is to check against *all* other products.
        for record in self:
            # Use exists() for robustness
            if (
                record.product_id.exists()
                and self.search_count(
                    [
                        ("barcode", "=", record.barcode),
                        (
                            "product_id",
                            "!=",
                            record.product_id.id,
                        ),  # Check against other products
                        # ('id', '!=', record.id) # Alternative: check against other records
                    ]
                )
                > 0
            ):
                # Consider a more general error message if enforcing global uniqueness:
                # raise ValidationError(_("Barcode '%s' already exists!", record.barcode))
                raise ValidationError(_("Barcode already exists for another product!"))

    @api.constrains("product_id", "uom_id")
    def _check_uom_category(self):
        """Validate that the barcode UoM is in the same category as the product's default UoM."""
        for record in self:
            # Use exists() for robustness
            if record.product_id.exists() and record.uom_id.exists():
                # Use the computed field for consistency
                product_uom_category = record.product_uom_category_id
                barcode_uom_category = record.uom_id.category_id
                if product_uom_category != barcode_uom_category:
                    raise ValidationError(
                        _(
                            "The Unit of Measure '%(uom_name)s' (Category: %(barcode_uom_category)s) "
                            "must belong to the same category as the product's default Unit of Measure "
                            "(Category: %(product_uom_category)s).",
                            uom_name=record.uom_id.name,
                            barcode_uom_category=barcode_uom_category.name,
                            product_uom_category=product_uom_category.name,
                        )
                    )

    @api.model
    def _load_pos_data_domain(self, data):
        return [("product_id.available_in_pos", "=", True)]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ["id", "barcode", "product_id", "uom_id", "price"]

    ENGLISH_CHARS = "0123456789."
    ARABIC_CHARS = "٠١٢٣٤٥٦٧٨٩٫"

    # Define the translation table once as a class attribute
    ARABIC_NUMERALS = str.maketrans(ENGLISH_CHARS, ARABIC_CHARS)

    @api.depends('price')  # <-- Crucial decorator must be present!
    def _compute_arabic_price_alt(self):
        # Access the class attribute
        translation_table = self.ARABIC_NUMERALS

        for rec in self:
            if rec.price is not None:
                # 1. Format the float to a string with 2 decimal places
                formatted = "{:.2f}".format(rec.price)

                # 2. Translate the entire formatted string in one go
                rec.arabic_price_alt = formatted.translate(translation_table)
            else:
                rec.arabic_price_alt = False
