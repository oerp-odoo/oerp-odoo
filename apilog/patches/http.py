import logging

from odoo.http import HttpDispatcher

from .. import value_objects as vo
from ..utils import get_env, to_werkzeug_response

orig_dispatch = HttpDispatcher.dispatch
orig_handle_error = HttpDispatcher.handle_error


_logger = logging.getLogger(__name__)


def handle_wsgi_logging(request, response):
    if not request.db:
        return
    try:
        with get_env(request.db) as env:
            env['apilog.handler'].handle(
                vo.RequestDirection.INCOMING,
                'wsgi',
                vo.ApilogRequest.from_httprequest(request.httprequest),
                vo.ApilogResponse.from_werkzeug_response(
                    to_werkzeug_response(response)
                ),
            )
    except Exception:
        _logger.error(
            "Something went wrong attempting to save incoming request as a log",
            stack_info=True,
        )


def dispatch(self, endpoint, args):
    res = orig_dispatch(self, endpoint, args)
    handle_wsgi_logging(self.request, res)
    return res


def handle_error(self, exc: Exception):
    res = orig_handle_error(self, exc)
    handle_wsgi_logging(self.request, res)
    return res


HttpDispatcher.dispatch = dispatch
HttpDispatcher.handle_error = handle_error
