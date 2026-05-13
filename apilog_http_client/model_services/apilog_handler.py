from __future__ import annotations

from odoo import SUPERUSER_ID, api, models
from odoo.tools import config

from odoo.addons.apilog import value_objects as vo


class ApilogHandler(models.AbstractModel):
    _inherit = 'apilog.handler'

    def handle_http_client(self, response, extra_vals=None):
        request = response.request
        args = (
            vo.RequestDirection.OUTGOING,
            'http_client',
            vo.ApilogRequest(
                endpoint=request.url,
                verb=request.method.upper(),
                _headers=request.headers,
                body=request.body or None,
            ),
            vo.ApilogResponse(
                status_code=response.status_code,
                _headers=response.headers,
                body=response.text or None,
            ),
        )
        if config['test_enable']:
            return self.env['apilog.handler'].handle(*args, extra_vals=extra_vals)
        else:
            with self.env.registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, dict(self.env.context))
                log = env['apilog.handler'].handle(*args, extra_vals=extra_vals)
                cr.commit()  # pylint: disable=invalid-commit
                return log
