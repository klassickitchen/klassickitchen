from odoo import api, models
from odoo.osv.expression import AND


class PosSession(models.Model):
    _inherit = "pos.session"

    def _load_pos_data_models(self, config_id):
        """Add product.barcode to the list of models loaded in POS"""
        models = super()._load_pos_data_models(config_id)
        models.append("product.barcode")
        return models

    def find_product_by_barcode(self, barcode, config_id):
        """Override to first check product.barcode model for multiple barcodes per company"""
        product_fields = self.env["product.product"]._load_pos_data_fields(config_id)
        product_packaging_fields = self.env["product.packaging"]._load_pos_data_fields(config_id)
        product_context = {**self.env.context, "display_default_code": False}

        current_company = self.env.company.id

        # 1️⃣ First check our custom product.barcode model
        product_barcode = self.env["product.barcode"].search(
            [
                ("barcode", "=", barcode),
                ("product_id.sale_ok", "=", True),
                ("product_id.available_in_pos", "=", True),
                "|",
                ("company_id", "=", current_company),  # match current company
                ("company_id", "=", False),  # or global (shared) barcodes
            ],
            limit=1,
        )

        if product_barcode and product_barcode.product_id:
            # Found in custom barcode model - return with custom price and UOM
            product_data = product_barcode.product_id.with_context(product_context).read(product_fields, load=False)
            if product_data:
                # Override the price with the barcode-specific price
                product_data[0]["lst_price"] = product_barcode.price
                # Add the custom barcode info for frontend processing
                product_data[0]["_barcode_uom_id"] = product_barcode.uom_id.id if product_barcode.uom_id else False
                product_data[0]["_barcode_price"] = product_barcode.price
                product_data[0]["_barcode_company_id"] = product_barcode.company_id.id

                return {"product.product": product_data}

        # 2️⃣ Fall back to standard product barcode check
        product = self.env["product.product"].search(
            [
                ("barcode", "=", barcode),
                ("sale_ok", "=", True),
                ("available_in_pos", "=", True),
            ],
            limit=1,
        )

        if product:
            return {
                "product.product": product.with_context(product_context).read(product_fields, load=False)
            }

        # 3️⃣ Check product packaging
        domain = [("barcode", "not in", ["", False])]
        loaded_data = self._context.get("loaded_data")
        if loaded_data:
            loaded_product_ids = [x["id"] for x in loaded_data["product.product"]]
            domain = AND([domain, [("product_id", "in", loaded_product_ids)]])

        packaging_params = {
            "search_params": {
                "domain": [("barcode", "=", barcode)] + domain,
                "fields": ["name", "barcode", "product_id", "qty"],
            },
        }
        packaging = self.env["product.packaging"].search(
            packaging_params["search_params"]["domain"]
        )

        if packaging and packaging.product_id:
            return {
                "product.product": packaging.product_id.with_context(product_context).read(product_fields, load=False),
                "product.packaging": packaging.read(product_packaging_fields, load=False),
            }
        else:
            return {
                "product.product": [],
                "product.packaging": [],
            }
