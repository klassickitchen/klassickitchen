# from odoo import models, fields, api, _
# from odoo.exceptions import UserError, ValidationError
# from collections import defaultdict
# import logging # Import logging
#
# _logger = logging.getLogger(__name__) # Setup logger
#
# class IntercompanyStockWizard(models.TransientModel):
#     _name = 'intercompany.stock.wizard'
#     _description = 'Intercompany Stock Wizard'
#
#     sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
#     order_line_ids = fields.One2many('intercompany.stock.wizard.line', 'wizard_id', string="Products to Purchase")
#
#     # @api.model_create_multi
#     # def create(self, vals):
#     #     print(vals,"valsss")
#     #     res = super().create(vals)
#     #     self.update_pricelist()
#     #     return res
#     def create_intercompany_purchase_order(self):
#         self.ensure_one()
#
#         selected_lines = self.order_line_ids.filtered(lambda l: l.selected)
#         if not selected_lines:
#             raise UserError(_("Please select at least one product line to purchase."))
#
#         lines_by_company = defaultdict(list)
#         for line in selected_lines:
#             if not line.company_id:
#                 raise UserError(_("Source Company is missing for product '%s'. Please select a company.",
#                                   line.p_product_id.display_name))
#             if not line.company_id.partner_id:
#                 raise UserError(
#                     _("The source company '%s' for product '%s' does not have an associated Partner record.",
#                       line.company_id.name, line.p_product_id.display_name))
#             # Group lines by company_id, storing the line itself in the list
#             lines_by_company[line.company_id].append(line)
#
#         created_po_ids = []
#         for company, lines in lines_by_company.items():
#             picking_type = self.env['stock.picking.type'].search([
#                 ('code', '=', 'incoming'),
#                 ('warehouse_id.company_id', '=', self.sale_order_id.company_id.id)
#             ], limit=1)
#             if not picking_type:
#                 raise UserError(_("No incoming picking type configured for the warehouse of company '%s'.",
#                                   self.sale_order_id.company_id.name))
#
#             po_vals = {
#                 'partner_id': company.partner_id.id,
#                 'company_id': self.sale_order_id.company_id.id,
#                 'origin': self.sale_order_id.name,
#                 'order_line': [(0, 0, {
#                     'p_product_id': line.p_product_id.id,
#                     'name': line.p_product_id.display_name,
#                     'product_qty': line.quantity,
#                     'price_unit': line.price_unit,
#                     'product_uom': line.p_product_id.uom_po_id.id or line.p_product_id.uom_id.id,
#                     'date_planned': fields.Datetime.now(),
#                 }) for line in lines],
#                 'picking_type_id': picking_type.id,
#             }
#             purchase_order = self.env['purchase.order'].create(po_vals)
#             created_po_ids.append(purchase_order.id)
#
#             purchase_order.button_confirm()
#
#         # --- Link PO(s) back to Sale Order ---
#         if created_po_ids and not self.sale_order_id.intercompany_purchase_order_id:
#             self.sale_order_id.write({
#                 'intercompany_purchase_order_id': created_po_ids[0]
#             })
#
#         # --- Confirm the original Sales Order ---
#         if self.sale_order_id.state in ('draft', 'sent'):
#             if not self.env.context.get('intercompany_po_confirming_so'):
#                 self.sale_order_id.with_context(intercompany_po_confirming_so=True).action_confirm()
#         elif self.sale_order_id.state == 'sale':
#             _logger.info(f"Sales Order {self.sale_order_id.name} was already confirmed.")
#             pass
#
#         # --- Return Action ---
#         if created_po_ids:
#             if len(created_po_ids) > 1:
#                 action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
#                 action['domain'] = [('id', 'in', created_po_ids)]
#                 return action
#             else:
#                 action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
#                 action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
#                 action['res_id'] = created_po_ids[0]
#                 return action
#         else:
#             return {'type': 'ir.actions.act_window_close'}
#         print("now it woerks",self.order_line_ids.p_product_id.id)
#
#     def create_intercompany_purchase_order_confirm(self):
#         self.ensure_one()
#         if not self.order_line_ids.filtered(lambda l: l.selected):
#             return
#
#         lines_by_company = defaultdict(list)
#         for line in self.order_line_ids.filtered(lambda l: l.selected):
#             _logger.info(f"Processing wizard line: {line.p_product_id.id}, {line.quantity}")
#
#             # Extract and store relevant data in a dictionary
#             line_data = {
#                 'p_product_id': line.p_product_id.id,
#                 'quantity': line.quantity,
#                 'price_unit': line.price_unit,
#                 'taxes_id': line.taxes_id.ids,
#                 'product_uom': line.p_product_id.uom_po_id.id or line.p_product_id.uom_id.id,  # Ensure product_uom is set
#                 'name': line.p_product_id.display_name,
#             }
#             lines_by_company[line.company_id.id].append(line_data)
#
#         created_po_ids = []
#
#         # Create purchase order for each company
#         for company_id, lines_data in lines_by_company.items():
#             purchase_order = self.env['purchase.order'].create({
#                 'partner_id': self.env['res.company'].browse(company_id).partner_id.id,
#                 'company_id': self.sale_order_id.company_id.id,
#                 'order_line': [(0, 0, {
#                     'p_product_id': data['p_product_id'],
#                     'name': data['name'],  # Explicitly set the name
#                     'product_qty': data['quantity'],
#                     'price_unit': data['price_unit'],
#                     'taxes_id': [(6, 0, data['taxes_id'])],
#                     'product_uom': data['product_uom'],
#                 }) for data in lines_data],
#             })
#
#             purchase_order.button_confirm()
#             created_po_ids.append(purchase_order.id)
#             for picking in purchase_order.picking_ids:
#                 for move in picking.move_ids:
#                     move.quantity_done = move.product_uom_qty
#
#             purchase_order.picking_ids.button_validate()
#
#         # link and confirm the original sales order
#         if created_po_ids and not self.sale_order_id.intercompany_purchase_order_id:
#             self.sale_order_id.write({
#                 'intercompany_purchase_order_id': created_po_ids[0]
#             })
#         self.sale_order_id.action_confirm()
#         print("now it woerks")
#
#
# class IntercompanyStockWizardLine(models.TransientModel):
#     _name = 'intercompany.stock.wizard.line'
#     _description = 'Intercompany Stock Wizard Line'
#
#     wizard_id = fields.Many2one('intercompany.stock.wizard', string="Wizard")
#     p_product_id = fields.Many2one('product.product', string='Product Purchase', required=True)
#     company_id = fields.Many2one(
#         'res.company',
#         string='Source Company',
#         required=True,
#         domain=lambda self: [('id', '!=', self.env.company.id)]
#     )
#     quantity = fields.Float(string='Quantity', required=True)
#     qty_available = fields.Float(string='Available Quantity', compute='_compute_qty_available')
#     price_unit = fields.Float(string="Unit Price")
#     taxes_id = fields.Many2many('account.tax', string="Taxes")
#     amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
#     selected = fields.Boolean(string="Select to Purchase", default=True)
#
#     def action_view_stock_details(self):
#         """Opens the Stock Details wizard for the product on this line."""
#         self.ensure_one()
#         if not self.p_product_id:
#             return {} # Do nothing if no product is selected
#
#         # Prepare the context for the stock details wizard
#         # It needs the product_id
#         ctx = {
#             'default_product_id': self.p_product_id.id,
#             # You might want to pass the original SO company if needed
#             # 'default_company_id': self.wizard_id.sale_order_id.company_id.id,
#         }
#
#         # Return the action to open the stock details wizard
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _('Stock Details for %s') % self.p_product_id.display_name,
#             'res_model': 'stock.details.wizard', # The model of the wizard to open
#             'view_mode': 'form',
#             'target': 'new', # Open as a pop-up dialog
#             'context': ctx,
#         }
#
#     @api.depends('quantity', 'price_unit')
#     def _compute_amount(self):
#         for line in self:
#             line.amount = line.quantity * line.price_unit
#
#     @api.depends('p_product_id', 'company_id')
#     def _compute_qty_available(self):
#         for line in self:
#             if line.p_product_id and line.company_id:
#                 product_in_company = line.p_product_id.with_company(line.company_id)
#                 line.qty_available = product_in_company.sudo().qty_available
#             else:
#                 line.qty_available = 0.0
#
#     @api.onchange('company_id', 'p_product_id')
#     def _onchange_company_product(self):
#         if self.company_id and self.p_product_id:
#             product_in_company = self.p_product_id.with_company(self.company_id)
#             self.price_unit = product_in_company.sudo().standard_price
#             self.taxes_id = [(6, 0, self.p_product_id.supplier_taxes_id.ids)]

# from odoo import models, fields, api
#
#
# class IntercompanyStockWizard(models.TransientModel):
#     _name = 'intercompany.stock.wizard'
#     _description = 'Intercompany Stock Wizard'
#
#     sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
#     company_id = fields.Many2one(
#         'res.company',
#         string='Source Company',
#         required=True,
#         domain=lambda self: [('id', '!=', self.env.company.id)]
#     )
#     order_line_ids = fields.One2many('intercompany.stock.wizard.line', 'wizard_id', string="Products to Purchase")
#
#     @api.onchange('company_id')
#     def _onchange_company_id(self):
#         if not self.company_id:
#             self.order_line_ids = [(5, 0, 0)]
#             return
#
#         products_to_purchase = []
#         sale_order = self.sale_order_id
#
#         for line in sale_order.order_line:
#             product = line.p_product_id
#             product_in_main_company = product.with_company(sale_order.company_id)
#             available_qty_in_main_company = product_in_main_company.sudo().qty_available
#
#             if available_qty_in_main_company < line.product_uom_qty:
#                 product_in_company = product.with_company(self.company_id)
#                 available_qty = product_in_company.sudo().qty_available
#
#                 if available_qty >= line.product_uom_qty:
#                     products_to_purchase.append((0, 0, {
#                         'p_product_id': product.id,
#                         'quantity': min(line.product_uom_qty, available_qty),
#                         'price_unit': product_in_company.standard_price,
#                         'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
#                         'selected': True
#                     }))
#
#         if products_to_purchase:
#             self.order_line_ids = [(5, 0, 0)] + products_to_purchase
#         else:
#             self.order_line_ids = [(5, 0, 0)]
#
#     def create_intercompany_purchase_order(self):
#         if not self.order_line_ids:
#             return
#
#         purchase_order = self.env['purchase.order'].create({
#             'partner_id': self.company_id.partner_id.id,
#             'company_id': self.sale_order_id.company_id.id,
#             'order_line': [(0, 0, {
#                 'p_product_id': line.p_product_id.id,
#                 'product_qty': line.quantity,
#                 'price_unit': line.price_unit,
#                 'taxes_id': [(6, 0, line.taxes_id.ids)]
#             }) for line in self.order_line_ids if line.selected],
#         })
#
#         purchase_order.button_confirm()
#
#         for picking in purchase_order.picking_ids:
#             for move in picking.move_ids:
#                 move.quantity_done = move.product_uom_qty
#
#         purchase_order.picking_ids.button_validate()
#
#         self.sale_order_id.action_confirm()
#
#         return {'type': 'ir.actions.act_window_close'}
#
#
# class IntercompanyStockWizardLine(models.TransientModel):
#     _name = 'intercompany.stock.wizard.line'
#     _description = 'Intercompany Stock Wizard Line'
#
#     wizard_id = fields.Many2one('intercompany.stock.wizard', string="Wizard")
#     p_product_id = fields.Many2one('product.product', string='Product', required=True)
#     quantity = fields.Float(string='Quantity', required=True)
#     price_unit = fields.Float(string="Unit Price")
#     taxes_id = fields.Many2many('account.tax', string="Taxes")
#     amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
#     selected = fields.Boolean(string="Select to Purchase", default=True)
#
#     @api.depends('quantity', 'price_unit')
#     def _compute_amount(self):
#         for line in self:
#             line.amount = line.quantity * line.price_unit


# from odoo import models, fields, api
#
#
# class IntercompanyStockWizard(models.TransientModel):
#     _name = 'intercompany.stock.wizard'
#     _description = 'Intercompany Stock Wizard'
#
#     sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
#     order_line_ids = fields.One2many('intercompany.stock.wizard.line', 'wizard_id', string="Products to Purchase")
#
#     @api.onchange('sale_order_id')
#     def _onchange_sale_order_id(self):
#         if not self.sale_order_id:
#             self.order_line_ids = [(5, 0, 0)]
#             return
#
#         products_to_purchase = []
#         sale_order = self.sale_order_id
#
#         for line in sale_order.order_line:
#             product = line.p_product_id
#             print("the prod",line.p_product_id.id)
#             product_in_main_company = product.with_company(sale_order.company_id)
#             available_qty_in_main_company = product_in_main_company.sudo().qty_available
#
#             if available_qty_in_main_company < line.product_uom_qty:
#                 products_to_purchase.append((0, 0, {
#                     'p_product_id': product.id,
#                     'quantity': line.product_uom_qty,
#                     'price_unit': product.standard_price,
#                     'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
#                     'selected': True
#                 }))
#
#         if products_to_purchase:
#             self.order_line_ids = [(5, 0, 0)] + products_to_purchase
#         else:
#             self.order_line_ids = [(5, 0, 0)]
#
#     def create_intercompany_purchase_order_confirm(self):
#         if not self.sale_order_id.filtered(lambda l: l.selected):
#             return
#
#         # Group lines by company
#         lines_by_company = {}
#         for line in self.order_line_ids.filtered(lambda l: l.selected):
#             if line.company_id.id not in lines_by_company:
#                 lines_by_company[line.company_id.id] = []
#             lines_by_company[line.company_id.id].append(line)
#
#         # Create purchase order for each company
#         for company_id, lines in lines_by_company.items():
#             purchase_order = self.env['purchase.order'].create({
#                 'partner_id': self.env['res.company'].browse(company_id).partner_id.id,
#                 'company_id': self.sale_order_id.company_id.id,
#                 'order_line': [(0, 0, {
#                     'p_product_id': line.p_product_id.id,
#                     'product_qty': line.quantity,
#                     'price_unit': line.price_unit,
#                     'taxes_id': [(6, 0, line.taxes_id.ids)]
#                 }) for line in lines],
#             })
#
#             purchase_order.button_confirm()
#
#             for picking in purchase_order.picking_ids:
#                 for move in picking.move_ids:
#                     move.quantity_done = move.product_uom_qty
#
#             purchase_order.picking_ids.button_validate()
#
#         self.sale_order_id.action_confirm()
#
#         return {'type': 'ir.actions.act_window_close'}
#
#
# class IntercompanyStockWizardLine(models.TransientModel):
#     _name = 'intercompany.stock.wizard.line'
#     _description = 'Intercompany Stock Wizard Line'
#
#     wizard_id = fields.Many2one('intercompany.stock.wizard', string="Wizard")
#     p_product_id = fields.Many2one('product.product', string='Product', required=True)
#     company_id = fields.Many2one(
#         'res.company',
#         string='Source Company',
#         required=True,
#         domain=lambda self: [('id', '!=', self.env.company.id)]
#     )
#     quantity = fields.Float(string='Quantity', required=True)
#     qty_available = fields.Float(string='Available Quantity', compute='_compute_qty_available')
#     price_unit = fields.Float(string="Unit Price")
#     taxes_id = fields.Many2many('account.tax', string="Taxes")
#     amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
#     selected = fields.Boolean(string="Select to Purchase", default=True)
#
#     @api.depends('quantity', 'price_unit')
#     def _compute_amount(self):
#         for line in self:
#             line.amount = line.quantity * line.price_unit
#
#     @api.depends('p_product_id', 'company_id')
#     def _compute_qty_available(self):
#         for line in self:
#             if line.p_product_id and line.company_id:
#                 product_in_company = line.p_product_id.with_company(line.company_id)
#                 line.qty_available = product_in_company.sudo().qty_available
#             else:
#                 line.qty_available = 0.0
#
#     @api.onchange('company_id', 'p_product_id')
#     def _onchange_company_product(self):
#         if self.company_id and self.p_product_id:
#             product_in_company = self.p_product_id.with_company(self.company_id)
#             self.price_unit = product_in_company.sudo().standard_price
#             self.taxes_id = [(6, 0, self.p_product_id.supplier_taxes_id.ids)]

# from odoo import models, fields, api
#
#
# class IntercompanyStockWizard(models.TransientModel):
#     _name = 'intercompany.stock.wizard'
#     _description = 'Intercompany Stock Wizard'
#
#     sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
#     company_id = fields.Many2one(
#         'res.company',
#         string='Source Company',
#         required=True,
#         domain=lambda self: [('id', '!=', self.env.company.id)]
#     )
#     order_line_ids = fields.One2many('intercompany.stock.wizard.line', 'wizard_id', string="Products to Purchase")
#
#     @api.onchange('company_id')
#     def _onchange_company_id(self):
#         if not self.company_id:
#             self.order_line_ids = [(5, 0, 0)]
#             return
#
#         products_to_purchase = []
#         sale_order = self.sale_order_id
#
#         for line in sale_order.order_line:
#             product = line.product_id
#             product_in_main_company = product.with_company(sale_order.company_id)
#             available_qty_in_main_company = product_in_main_company.sudo().qty_available
#
#             if available_qty_in_main_company < line.product_uom_qty:
#                 product_in_company = product.with_company(self.company_id)
#                 available_qty = product_in_company.sudo().qty_available
#
#                 if available_qty >= line.product_uom_qty:
#                     products_to_purchase.append((0, 0, {
#                         'product_id': product.id,
#                         'quantity': min(line.product_uom_qty, available_qty),
#                         'price_unit': product_in_company.standard_price,
#                         'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
#                         'selected': True
#                     }))
#
#         if products_to_purchase:
#             self.order_line_ids = [(5, 0, 0)] + products_to_purchase
#         else:
#             self.order_line_ids = [(5, 0, 0)]
#
#     def create_intercompany_purchase_order(self):
#         if not self.order_line_ids:
#             return
#         created_po_ids = []
#         purchase_order = self.env['purchase.order'].create({
#             'partner_id': self.company_id.partner_id.id,
#             'company_id': self.sale_order_id.company_id.id,
#             'order_line': [(0, 0, {
#                 'product_id': line.product_id.id,
#                 'product_qty': line.quantity,
#                 'price_unit': line.price_unit,
#                 'taxes_id': [(6, 0, line.taxes_id.ids)]
#             }) for line in self.order_line_ids if line.selected],
#         })
#         print(purchase_order,"order order")
#         purchase_order.button_confirm()
#         created_po_ids.append(purchase_order.id)
#
#         for picking in purchase_order.picking_ids:
#             for move in picking.move_ids:
#                 move.quantity = move.product_uom_qty
#
#         purchase_order.picking_ids.button_validate()
#
#         self.sale_order_id.action_confirm()
#
#         return {'type': 'ir.actions.act_window_close'}
#
#
# class IntercompanyStockWizardLine(models.TransientModel):
#     _name = 'intercompany.stock.wizard.line'
#     _description = 'Intercompany Stock Wizard Line'
#
#     wizard_id = fields.Many2one('intercompany.stock.wizard', string="Wizard")
#     product_id = fields.Many2one('product.product', string='Product', required=True)
#     company_id = fields.Many2one(
#         'res.company',
#         string='Source Company Line',
#         required=True,
#         domain=lambda self: [('id', '!=', self.env.company.id)]
#     )
#     quantity = fields.Float(string='Quantity', required=True)
#     price_unit = fields.Float(string="Unit Price")
#     taxes_id = fields.Many2many('account.tax', string="Taxes")
#     amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
#     selected = fields.Boolean(string="Select to Purchase", default=True)
#
#     @api.depends('quantity', 'price_unit')
#     def _compute_amount(self):
#         for line in self:
#             line.amount = line.quantity * line.price_unit


# sonet

from odoo import models, fields, api


class IntercompanyStockWizard(models.TransientModel):
    _name = 'intercompany.stock.wizard'
    _description = 'Intercompany Stock Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    order_line_ids = fields.One2many('intercompany.stock.wizard.line', 'wizard_id', string="Products to Purchase")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if res.get('order_line_ids'):
            new_lines = []
            for line_vals in res['order_line_ids']:
                if line_vals[0] != 0:
                    new_lines.append(line_vals)
                    continue

                vals = line_vals[2]
                product = self.env['product.product'].browse(vals['product_id'])
                companies = self.env['res.company'].search([('id', '!=', self.env.company.id)])
                available_companies = []
                for company in companies:
                    p = product.with_company(company).sudo()
                    if p.free_qty > 0:
                        available_companies.append({
                            'company': company,
                            'free_qty': p.free_qty,
                            'qty_available': p.qty_available,
                            'price_unit': p.standard_price,
                        })

                if available_companies:
                    selected_company = sorted(available_companies, key=lambda x: x['free_qty'], reverse=True)[0]
                    vals.update({
                        'company_id': selected_company['company'].id,
                        'qty_available': selected_company['qty_available'],
                        'free_quantity': selected_company['free_qty'],
                        'price_unit': selected_company['price_unit'],
                    })
                else:
                    vals.update({
                        'company_id': False,
                        'qty_available': 0.0,
                        'free_quantity': 0.0,
                        'price_unit': product.standard_price,
                    })
                new_lines.append((0, 0, vals))
            res['order_line_ids'] = new_lines
        return res

    def create_intercompany_purchase_order_confirm(self):
        if not self.order_line_ids.filtered(lambda l: l.selected):
            return

        created_po_ids = []
        company_lines = {}

        for line in self.order_line_ids.filtered(lambda l: l.selected):
            if line.company_id.id not in company_lines:
                company_lines[line.company_id.id] = []
            company_lines[line.company_id.id].append(line)

        # Create a purchase order for each company
        for company_id, lines in company_lines.items():
            purchase_order = self.env['purchase.order'].create({
                'partner_id': self.env['res.company'].browse(company_id).partner_id.id,
                'company_id': self.sale_order_id.company_id.id,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'taxes_id': [(6, 0, line.taxes_id.ids)]
                }) for line in lines],
            })

            purchase_order.button_confirm()
            created_po_ids.append(purchase_order.id)

            for picking in purchase_order.picking_ids:
                for move in picking.move_ids:
                    move.quantity = move.product_uom_qty

            purchase_order.picking_ids.button_validate()

        if created_po_ids:
            self.sale_order_id.write({
                'intercompany_purchase_order_ids': [(6, 0, created_po_ids)]
            })

        self.sale_order_id.action_confirm()

        return {'type': 'ir.actions.act_window_close'}

    def create_intercompany_purchase_order(self):
        if not self.order_line_ids.filtered(lambda l: l.selected):
            return

        created_po_ids = []

        company_lines = {}

        for line in self.order_line_ids.filtered(lambda l: l.selected):
            if line.company_id.id not in company_lines:
                company_lines[line.company_id.id] = []
            company_lines[line.company_id.id].append(line)

        # Create a purchase order for each company
        for company_id, lines in company_lines.items():
            purchase_order = self.env['purchase.order'].create({
                'partner_id': self.env['res.company'].browse(company_id).partner_id.id,
                'company_id': self.sale_order_id.company_id.id,
                'order_line': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'taxes_id': [(6, 0, line.taxes_id.ids)]
                }) for line in lines],
            })

            purchase_order.button_confirm()
            created_po_ids.append(purchase_order.id)



        if created_po_ids:
            self.sale_order_id.write({
                'intercompany_purchase_order_ids': [(6, 0, created_po_ids)]
            })

        self.sale_order_id.action_confirm()

        return {'type': 'ir.actions.act_window_close'}


class IntercompanyStockWizardLine(models.TransientModel):
    _name = 'intercompany.stock.wizard.line'
    _description = 'Intercompany Stock Wizard Line'

    wizard_id = fields.Many2one('intercompany.stock.wizard', string="Wizard")
    product_id = fields.Many2one('product.product', string='Product', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Source Company',
        required=True,
        domain=lambda self: [('id', '!=', self.env.company.id)]
    )
    qty_available = fields.Float(string='On Hand Quantity', readonly=True)
    free_quantity = fields.Float(string='Free quantity', readonly=True,
                                 help="Quantity that is available and not reserved")

    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Float(string="Unit Price")
    taxes_id = fields.Many2many('account.tax', string="Taxes")
    amount = fields.Float(string="Amount", compute="_compute_amount", store=True)
    selected = fields.Boolean(string="Select to Purchase", default=True)

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit


    @api.onchange('company_id', 'product_id')
    def _onchange_company_product(self):
        if self.company_id and self.product_id:
            product_with_company = self.product_id.with_company(self.company_id)
            self.qty_available = product_with_company.sudo().qty_available
            self.free_quantity = product_with_company.sudo().free_qty
            self.price_unit = product_with_company.sudo().standard_price