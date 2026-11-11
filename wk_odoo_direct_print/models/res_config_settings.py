# -*- coding: utf-8 -*-

from odoo import models

from ..hooks import ensure_advance_automation_menu


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_recreate_advance_automation_menu(self):
        self.ensure_one()
        module = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'base_automation')
        ], limit=1)
        if not module:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'Base Automation module was not found in Apps list. Update Apps List and retry.',
                    'type': 'warning',
                    'sticky': False,
                },
            }
        if module and module.state != 'installed':
            module.button_immediate_install()

        created = ensure_advance_automation_menu(self.env)
        if not created:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'Base Automation could not be installed automatically. Please install it and retry.',
                    'type': 'warning',
                    'sticky': False,
                },
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Base Automation is ready and Advance Automation Rule menu is created.',
                'type': 'success',
                'sticky': False,
            },
        }
