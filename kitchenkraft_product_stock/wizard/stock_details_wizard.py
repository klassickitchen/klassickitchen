from odoo import models, fields, api

class StockDetailsWizard(models.TransientModel):
    _name = 'stock.details.wizard'
    _description = 'Stock Details Wizard'

    product_id = fields.Many2one('product.product', string='Product', required=True, readonly=True)
    stock_line_ids = fields.One2many('stock.details.line', 'wizard_id', string='Stock Details')

    @api.model
    def default_get(self, fields_list):
        res = super(StockDetailsWizard, self).default_get(fields_list)
        if self.env.context.get('default_product_id'):
            product_id = self.env.context['default_product_id']
            stock_lines = []
            companies = self.env['res.company'].search([])


            for company in companies:
                stock_quant = self.env['stock.quant'].sudo().search([
                    ('product_id', '=', product_id),
                    ('company_id', '=', company.id)
                ], limit=1)

                print(stock_quant,"sqqqqqq")

                print(company.name,"forrr",product_id)

                print(product_id,"Gggggggg")
                stock_lines.append((0, 0, {
                    'company_id': company.id,
                    'quantity': stock_quant.quantity if stock_quant else 0.0,
                }))

            res['stock_line_ids'] = stock_lines
            res['product_id'] = product_id
        return res


class StockDetailsLine(models.TransientModel):
    _name = 'stock.details.line'
    _description = 'Stock Details Line'

    wizard_id = fields.Many2one('stock.details.wizard', string='Wizard', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True)
    quantity = fields.Float(string='Quantity', readonly=True)