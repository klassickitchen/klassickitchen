from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    # Discount product lines now count as 0 in the (stored) gross, so recompute the
    # existing invoices that carry one; their Discount row then includes that line.
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env['account.move.line'].search([
        ('display_type', 'in', ('product', 'cogs')),
        ('product_id.product_tmpl_id.is_discount', '=', True),
    ])
    if not lines:
        return
    env.add_to_compute(lines._fields['amount_without_discount'], lines)
    env.add_to_compute(lines.move_id._fields['gross_total'], lines.move_id)
    env.flush_all()
