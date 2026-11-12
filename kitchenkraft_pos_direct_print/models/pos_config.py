# -*- coding: utf-8 -*-

import random
from odoo import api, fields, models
from odoo.tools.translate import _
import base64
from PIL import Image
from io import BytesIO
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

try:
    from escpos.printer import Dummy
except ImportError:
    Dummy = None
    _logger.warning("python-escpos not installed; ESC/POS dummy rasterizer unavailable.")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_direct_print = fields.Boolean(string='Use Direct Print')
    direct_printer_id = fields.Many2one(
        'wk.printer', string="Receipt Printer", help="Receipt Printer for print POS payment Receipt")
    receipt_print_auto = fields.Boolean(
        string='Automatic Receipt Printing via Receipt Printer', default=False,
        help='The receipt will automatically be printed via Receipt Printer at the open of Receipt Screen.')
    invoice_operation = fields.Selection([
        ('download', 'Download'),
        ('print', 'Print From Printer')
    ], string="Invoice Operation", default='download')
    selected_invoice_printer = fields.Many2one(
        'wk.printer',
        string="Invoice Printer")
    order_receipt_format = fields.Selection(
        [('xml', 'XML Receipt'), ('default', 'Default Receipt')],
        string="Order Receipt Format", default='xml', required=True)

    def get_direct_printer_info(self):
        printer_info = self.direct_printer_id._get_printer_config()
        printer_info.update({
            'is_hostmachine_online': self.direct_printer_id.hostmachine_id.is_online,
            'pos_cashdrawer': self.direct_printer_id.pos_cashdrawer, 
            'pending_print_jobs': len(self.env['print.jobs'].search([
                ('printer_id', '=', self.direct_printer_id.id),
                ('state', '!=', 'Done')
            ])),
        })
        return printer_info

    def get_invoice_printer_info(self):
        printer_info = self.selected_invoice_printer._get_printer_config()
        printer_info.update({
            'is_hostmachine_online': self.direct_printer_id.hostmachine_id.is_online,
            'pos_cashdrawer': self.direct_printer_id.pos_cashdrawer,
            'pending_print_jobs': len(self.env['print.jobs'].search([
                ('printer_id', '=', self.selected_invoice_printer.id),
                ('state', '!=', 'Done')
            ])),
        })
        return printer_info

    def print_invoice_documents_printer(self, invoice_ids):
        pdf = self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices", invoice_ids)[0]
        rendered_text = base64.b64encode(pdf)
        self.env['print.jobs'].create_print_job(
            self.selected_invoice_printer.id,
            'print-file',
            rendered_text,
            file_extension='pdf'
        )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_use_direct_print = fields.Boolean(
        related='pos_config_id.use_direct_print', readonly=False)
    pos_direct_printer_id = fields.Many2one(
        related='pos_config_id.direct_printer_id', readonly=False)
    pos_receipt_print_auto = fields.Boolean(
        related='pos_config_id.receipt_print_auto', readonly=False)
    pos_invoice_operation = fields.Selection(
        related='pos_config_id.invoice_operation', readonly=False)
    pos_selected_invoice_printer = fields.Many2one(
        related='pos_config_id.selected_invoice_printer', readonly=False)
    pos_order_receipt_format = fields.Selection(
        related='pos_config_id.order_receipt_format', readonly=False)


class PrintJobs(models.Model):
    _inherit = "print.jobs"
    
    def create_print_and_cashdrawer_job(self, printer_id, method, content, file_extension=None, is_byte_stream=False):
        # Open Cash Drawer pulse
        receipt_parts = [{
            "type": "escpos",
            "content": '\x1b\x70\x00\x19\xfa',
        }, {
            "type": "escpos",
            "content": '\x1B\x40',
        }, {
            "type": "escpos",
            "content": '\x1D\x56\x00',
        }]
        self.create_print_job(printer_id, 'print-complex', receipt_parts, None, False)
        # Send receipt print job
        self.create_print_job(printer_id, method, content, file_extension, is_byte_stream)
    
    def create_print_job(self, printer_id, method, content, file_extension=None, is_byte_stream=False):
        vals = {
            'printer_id': printer_id,
            'method': method,
            'content': content,
            'file_extension': file_extension,
            'is_byte_stream': is_byte_stream,
        }
        new_print_job = self.create(vals)

        current_version = new_print_job.printer_id.hostmachine_id.app_version or '2.0.18'
        old_version = [int(x) for x in '2.0.11'.split('.')]
        current_version = [int(x) for x in current_version.split('.')]
        length = max(len(old_version), len(current_version))
        old_version.extend([0] * (length - len(old_version)))
        current_version.extend([0] * (length - len(current_version)))

        if new_print_job.method == 'print-complex':
            content_list = literal_eval(new_print_job.content)
            for i, item in enumerate(content_list):
                if item.get('type') == 'image' and item.get('content'):
                    image_data = base64.b64decode(item['content'])
                    image_file = BytesIO(image_data)
                    img = Image.open(image_file)
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode == 'RGBA':
                        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        img = Image.alpha_composite(background, img)
                    img = img.convert('RGB')
                    try:
                        resample_filter = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample_filter = Image.ANTIALIAS

                    max_width = 530
                    if img.width > max_width:
                        img.thumbnail((max_width, 9999), resample_filter)

                    if Dummy:
                        img_bw = img.convert('1')
                        p = Dummy()
                        p.profile.media['width']['pixels'] = img.width
                        p.set(align='center')
                        p.image(img_bw)
                        p.set(align='left')
                        if current_version > old_version:
                            item['content'] = str(p.output)
                        else:
                            item['content'] = p.output
            new_print_job.content = content_list

        if new_print_job.method == 'print-image' and current_version > old_version:
            image_data = base64.b64decode(new_print_job.content)
            image_file = BytesIO(image_data)
            img = Image.open(image_file)
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                img = Image.alpha_composite(background, img)
            img = img.convert('RGB')
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.ANTIALIAS

            max_width = 530
            if img.width > max_width:
                img.thumbnail((max_width, 9999), resample_filter)

            if Dummy:
                img_bw = img.convert('1')
                p = Dummy()
                p.profile.media['width']['pixels'] = img.width
                p.image(img_bw)
                new_print_job.content = str(p.output)
                new_print_job.is_dummy = True

        msg_id = random.randint(999, 1_999_999_999)
        for each_partner in new_print_job.printer_id.hostmachine_id.user_ids:
            message = {'Persona': [{
                'id': msg_id,
                'im_status': 'print direct',
                'type': 'partner',
                'data': {
                    'method': 'print-job-cmd',
                    'host_id': new_print_job.printer_id.hostmachine_id.host_id,
                    'record_id': new_print_job.id
                }
            }]}
            self.env['bus.bus']._sendone(
                each_partner.partner_id,
                "mail.record/insert",
                message
            )
        return new_print_job


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['logo']


class WkPrinter(models.Model):
    _inherit = "wk.printer"

    pos_cashdrawer = fields.Boolean('Cash Drawer (Point Of Sale)', default=True)
