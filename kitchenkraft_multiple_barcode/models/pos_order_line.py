from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Product UoM",
        related=False,
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure product_uom_id is set properly"""
        for vals in vals_list:
            # If product_uom_id is not set but we have a product_id,
            # use the product's UoM
            if not vals.get("product_uom_id") and vals.get("product_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                if product and product.uom_id:
                    vals["product_uom_id"] = product.uom_id.id

        return super().create(vals_list)

    def write(self, vals):
        """Override write to ensure product_uom_id is set properly"""
        # If product_uom_id is being unset but we have a product_id,
        # use the product's UoM
        if "product_uom_id" in vals and not vals["product_uom_id"]:
            for line in self:
                if line.product_id and line.product_id.uom_id:
                    vals["product_uom_id"] = line.product_id.uom_id.id
                    break

        return super().write(vals)

    @api.model
    def default_get(self, fields_list):
        """Ensure product_uom_id is set when creating from UI"""
        defaults = super().default_get(fields_list)

        if "product_id" in defaults and defaults["product_id"]:
            product = self.env["product.product"].browse(defaults["product_id"])
            if product and product.uom_id and "product_uom_id" not in defaults:
                defaults["product_uom_id"] = product.uom_id.id

        return defaults

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Add product_uom_id to the fields loaded in POS since it's no longer
        a related field"""
        fields = super()._load_pos_data_fields(config_id)
        fields.append("product_uom_id")
        return fields
