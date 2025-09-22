from odoo import http
from odoo.http import request


class UiPython(http.Controller):

    @http.route('/my-route', type='http', auth='public', website=True)
    def execute_method(self, **kw):
            code = kw.get('python_code')
            # execute the code
            # ...