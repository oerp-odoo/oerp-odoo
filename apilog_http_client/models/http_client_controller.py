import logging

from odoo import models

_logger = logging.getLogger(__name__)


class HttpClientController(models.AbstractModel):
    _inherit = 'http.client.controller'

    def _check_response(self, response, options=None):
        if options is None:
            options = {}
        extra_log_vals = options.get('extra_log_vals', {})
        try:
            self.env['apilog.handler'].sudo().handle_http_client(
                response,
                extra_vals={
                    'res_model': extra_log_vals.get('res_model'),
                    'res_id': extra_log_vals.get('res_id'),
                },
            )
        except Exception:
            _logger.error("Could not handle HTTP Client logging", stack_info=True)
        return super()._check_response(response, options=options)
