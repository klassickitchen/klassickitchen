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
    arabic_price_alt = fields.Char(compute="_compute_arabic_price_alt", store=False)
    company_id = fields.Many2one("res.company", "Company")
    _sql_constraints = [
        (
            "barcode_unique_per_company",
            "unique(barcode, product_id, company_id)",
            "Barcode must be unique per product within a company!",
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

    @api.model
    def load(self, fields, data):
        return super(ProductBarcode, self.sudo()).load(fields, data)

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("import_file"):
            return super(ProductBarcode, self.sudo()).create(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        if self.env.context.get("import_file"):
            return super(ProductBarcode, self.sudo()).write(vals)
        return super().write(vals)


    @api.constrains("price")
    def _check_price_not_negative(self):
        for record in self:
            if record.price < 0:
                raise ValidationError(_("Price cannot be negative."))

    @api.constrains("barcode", "company_id")
    def _check_barcode_is_unique_per_company(self):
        for record in self:
            if not record.barcode or not record.company_id:
                continue

            duplicate_count = self.sudo().search_count(
                [
                    ("barcode", "=", record.barcode),
                    ("company_id", "=", record.company_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if duplicate_count > 0:
                raise ValidationError(
                    _(
                        "Barcode '%s' already exists for another product in company '%s'."
                    )
                    % (record.barcode, record.company_id.display_name)
                )

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

    # @api.model
    # def _load_pos_data_domain(self, data):
    #     return [("product_id.available_in_pos", "=", True)]

    @api.model
    def _load_pos_data_domain(self, data):
        return [
            ("product_id.available_in_pos", "=", True),
            ("company_id", "=", self.env.company.id),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ["id", "barcode", "product_id", "uom_id", "price"]

    ENGLISH_CHARS = "0123456789."
    ARABIC_CHARS = "٠١٢٣٤٥٦٧٨٩٫"

    # Define the translation table once as a class attribute
    ARABIC_NUMERALS = str.maketrans(ENGLISH_CHARS, ARABIC_CHARS)

    @api.depends("price")  # <-- Crucial decorator must be present!
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

    def action_open_label_layout2(self):
        # function for only alternative barcode
        self.ensure_one()
        product_tmpl = self.product_id.product_tmpl_id

        # create the wizard record manually
        wizard = self.env["product.label.layout"].create({
            "product_tmpl_ids": [(6, 0, [product_tmpl.id])],
            "print_format": "dymo",
        })

        # open it with context so your barcode info travels along
        return {
            "name": _("Product Labels"),
            "type": "ir.actions.act_window",
            "res_model": "product.label.layout",
            "view_mode": "form",
            "target": "new",
            "res_id": wizard.id,
            "context": {
                **self.env.context,
                "active_model": "product.template",
                "active_ids": [product_tmpl.id],
                "active_id": product_tmpl.id,
                "default_barcode": self.barcode,
                "from_alternative_barcode": True,
            },
        }
