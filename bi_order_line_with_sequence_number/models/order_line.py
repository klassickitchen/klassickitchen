# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_sequence_number = fields.Integer(
        string="No.", compute="_compute_sale_sequence_number", store=True
    )

    @api.depends(
        "order_id.order_line",
        "order_id.order_line.sequence",
        "order_id.order_line.display_type",
    )
    def _compute_sale_sequence_number(self):
        # Default so every record in self gets a value (e.g. lines without an
        # order or section/note lines).
        self.sale_sequence_number = 0
        for order in self.order_id:
            number = 1
            for line in order.order_line:
                if not line.display_type:
                    line.sale_sequence_number = number
                    number += 1


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_sequence_number = fields.Integer(
        string="No.", compute="_compute_purchase_sequence_number", store=True
    )

    @api.depends(
        "order_id.order_line",
        "order_id.order_line.sequence",
        "order_id.order_line.display_type",
    )
    def _compute_purchase_sequence_number(self):
        self.purchase_sequence_number = 0
        for order in self.order_id:
            number = 1
            for line in order.order_line:
                if not line.display_type:
                    line.purchase_sequence_number = number
                    number += 1


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Kept as Char (matches the previously installed column type, so no risky
    # column type migration on upgrade). Only product lines are numbered.
    invoice_sequence_number = fields.Char(
        string="No.", compute="_compute_invoice_sequence_number", store=True
    )

    @api.depends(
        "move_id.invoice_line_ids",
        "move_id.invoice_line_ids.sequence",
        "move_id.invoice_line_ids.display_type",
    )
    def _compute_invoice_sequence_number(self):
        self.invoice_sequence_number = ""
        for move in self.move_id:
            number = 1
            # The invoice report displays the lines sorted by sequence, so
            # number them in the same order to keep the column contiguous.
            for line in move.invoice_line_ids.sorted(key=lambda l: l.sequence):
                if line.display_type == "product":
                    line.invoice_sequence_number = str(number)
                    number += 1


class StockMove(models.Model):
    _inherit = "stock.move"

    stock_move_sequence = fields.Integer(
        string="No.", compute="_compute_stock_move_sequence", store=True
    )
    mrp_sequence_no = fields.Integer(
        string="No.", compute="_compute_mrp_sequence_no", store=True
    )

    @api.depends(
        "sale_line_id",
        "sale_line_id.sale_sequence_number",
        "purchase_line_id",
        "purchase_line_id.purchase_sequence_number",
        "picking_id",
        "picking_id.move_ids_without_package",
        "picking_id.move_ids_without_package.sequence",
    )
    def _compute_stock_move_sequence(self):
        # Position of each move inside its picking, used as a fallback for
        # moves that are not linked to a sale/purchase line (e.g. internal
        # transfers, manual receipts).
        position = {}
        for picking in self.picking_id:
            idx = 1
            for move in picking.move_ids_without_package:
                position[move.id] = idx
                idx += 1
        for move in self:
            if move.sale_line_id:
                # Carry the sale order line number onto the delivery.
                move.stock_move_sequence = move.sale_line_id.sale_sequence_number
            elif move.purchase_line_id:
                # Carry the purchase order line number onto the receipt.
                move.stock_move_sequence = (
                    move.purchase_line_id.purchase_sequence_number
                )
            else:
                move.stock_move_sequence = position.get(move.id, 0)

    @api.depends(
        "raw_material_production_id",
        "raw_material_production_id.move_raw_ids",
        "raw_material_production_id.move_raw_ids.sequence",
    )
    def _compute_mrp_sequence_no(self):
        self.mrp_sequence_no = 0
        for production in self.raw_material_production_id:
            number = 1
            for move in production.move_raw_ids:
                move.mrp_sequence_no = number
                number += 1


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    purchase_requistion_sequence = fields.Integer(
        string="No.", compute="_compute_purchase_requistion_sequence", store=True
    )

    @api.depends("requisition_id", "requisition_id.line_ids")
    def _compute_purchase_requistion_sequence(self):
        self.purchase_requistion_sequence = 0
        for requisition in self.requisition_id:
            number = 1
            for line in requisition.line_ids:
                line.purchase_requistion_sequence = number
                number += 1
