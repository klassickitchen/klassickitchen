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

            for company_id, lines in company_lines.items():
                company = self.env['res.company'].browse(company_id)

                purchase_order = self.env['purchase.order'].create({
                    'partner_id': company.partner_id.id,
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



        return {'type': 'ir.actions.act_window_close'}



    @api.model
    def _create_sale_order_from_po(self):
        # Let Odoo create the quotation
        sale_order = super()._create_sale_order_from_po()

        # Confirm it automatically
        if sale_order and sale_order.state in ['draft', 'sent']:
            sale_order.action_confirm()

            # Optionally validate delivery
            for picking in sale_order.picking_ids:
                for move in picking.move_ids_without_package:
                    move.quantity_done = move.product_uom_qty
                picking.button_validate()

        return sale_order


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

    def action_confirm_without_po(self):
        print('cheeeeee')
        """Confirm the Sale Order normally, bypass intercompany workflow, and generate deliveries."""
        sale_order = self.sale_order_id

        if sale_order.state in ['draft', 'sent']:
            # Use context flag to skip intercompany logic in your SaleOrder.action_confirm override
            sale_order.with_context(skip_intercompany=True).sudo().action_confirm()

        # Close the wizard
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
