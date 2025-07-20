from odoo import SUPERUSER_ID, api

from odoo.addons.base_rest import http

from ..const import CFG_PARAM_EXCEPTION_DESCRIPTION_NO_HTML

orig_wrapJsonException = http.wrapJsonException
orig_handle_exception = http.HttpRestRequest._handle_exception


def wrapJsonException(exception, include_description=False, extra_info=None):
    # Propagate to werkzeug exception!
    if getattr(wrapJsonException, '_description_without_html', None):
        exception._description_without_html = True
    return orig_wrapJsonException(
        exception, include_description=include_description, extra_info=extra_info
    )


def _handle_exception(self, exception):
    with self.env.registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env['ir.config_parameter'].get_param(
            CFG_PARAM_EXCEPTION_DESCRIPTION_NO_HTML
        ):
            # NOTE. We attach attribute to wrapJsonException function
            # directly so we could propagate it inside, because exception
            # here is not werkzeug exception (it is odoo one) and we need
            # to propagate that when werkzeug exception is instantiated!
            wrapJsonException._description_without_html = True
            res = orig_handle_exception(self, exception)
            # Clean up.
            del wrapJsonException._description_without_html
            return res
    return orig_handle_exception(self, exception)


http.HttpRestRequest._handle_exception = _handle_exception
http.wrapJsonException = wrapJsonException
