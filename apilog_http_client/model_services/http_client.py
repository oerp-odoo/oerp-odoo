import logging

from odoo import models

from odoo.addons.http_client.value_objects.request import RequestInput

_logger = logging.getLogger(__name__)


class HttpClient(models.AbstractModel):
    _inherit = 'http.client'

    def _check_response(self, response, inp: RequestInput):
        log_vals = inp.options.get('apilog_vals', {})
        try:
            self.env['apilog.handler'].sudo().handle_http_client(
                response,
                extra_vals={
                    'res_model': log_vals.get('res_model'),
                    'res_id': log_vals.get('res_id'),
                },
            )
        except Exception:
            _logger.error("Could not handle HTTP Client logging", stack_info=True)
        return super()._check_response(response, inp)
