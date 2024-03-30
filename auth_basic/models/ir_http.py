import logging

from odoo import SUPERUSER_ID, models
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)

AUTH_HEADER_KEY = 'HTTP_AUTHORIZATION'
AUTH_CREDENTIALS_PREFIX = 'Basic '


class IrHttp(models.AbstractModel):
    """Extend to add basic authentication method."""

    _inherit = "ir.http"

    @classmethod
    def _auth_method_basic(cls):
        headers = request.httprequest.environ
        credentials = headers.get(AUTH_HEADER_KEY, '')
        if credentials.startswith(AUTH_CREDENTIALS_PREFIX):
            request.uid = SUPERUSER_ID
            # We check credentials value without standard prefix.
            credentials = credentials[len(AUTH_CREDENTIALS_PREFIX) :]
            auth_basic = request.env["auth.basic"]._retrieve_auth_basic(credentials)
            # reset _env on the request since we change the uid, the
            # next call to env will instantiate an new
            # odoo.api.Environment with the user defined on the
            # auth.basic
            request._env = None
            request.uid = auth_basic.user_id.id
            request.auth_basic = auth_basic
            request.auth_basic_id = auth_basic.id
            return True
        _logger.error("Wrong %s, access denied", AUTH_HEADER_KEY)
        raise AccessDenied()
