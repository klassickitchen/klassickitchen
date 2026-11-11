# -*- coding: utf-8 -*-


def ensure_advance_automation_menu(env):
    base_automation_installed = bool(
        env['ir.module.module'].sudo().search_count([
            ('name', '=', 'base_automation'),
            ('state', '=', 'installed'),
        ])
    )
    if not base_automation_installed:
        return False

    parent_menu = env.ref('wk_odoo_direct_print.direct_printer_Automation', raise_if_not_found=False)
    base_automation_action = env.ref('base_automation.base_automation_act', raise_if_not_found=False)
    if not parent_menu or not base_automation_action:
        return False

    xmlid = 'wk_odoo_direct_print.menu_advance_automation_rule'
    existing_menu = env.ref(xmlid, raise_if_not_found=False)
    action_ref = 'ir.actions.act_window,%s' % base_automation_action.id
    vals = {
        'name': 'Advance Automation Rule',
        'parent_id': parent_menu.id,
        'sequence': 4,
        'action': action_ref,
    }

    # Reuse any previously created identical menu (for example from bridge addon)
    # and remove duplicates so users see only one menu entry.
    duplicate_menus = env['ir.ui.menu'].sudo().search([
        ('parent_id', '=', parent_menu.id),
        ('name', '=', 'Advance Automation Rule'),
        ('action', '=', action_ref),
    ], order='id asc')
    if duplicate_menus:
        keeper = existing_menu if existing_menu and existing_menu in duplicate_menus else duplicate_menus[0]
        keeper.sudo().write(vals)
        extras = duplicate_menus - keeper
        if extras:
            extras.sudo().unlink()

        if not existing_menu:
            env['ir.model.data'].sudo().create({
                'module': 'wk_odoo_direct_print',
                'name': 'menu_advance_automation_rule',
                'model': 'ir.ui.menu',
                'res_id': keeper.id,
                'noupdate': True,
            })
        return True

    if existing_menu:
        existing_menu.sudo().write(vals)
        return True

    menu = env['ir.ui.menu'].sudo().create(vals)
    env['ir.model.data'].sudo().create({
        'module': 'wk_odoo_direct_print',
        'name': 'menu_advance_automation_rule',
        'model': 'ir.ui.menu',
        'res_id': menu.id,
        'noupdate': True,
    })
    return True
