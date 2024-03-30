from unittest.mock import patch

from odoo.exceptions import AccessDenied, ValidationError
from odoo.tools.misc import mute_logger

from ..models.ir_http import AUTH_HEADER_KEY
from . import common

PATCH_PATH = 'odoo.addons.auth_basic.models.ir_http.request'


class _MockedRequest:
    pass


class _MockedHttpRequest:
    def __init__(self, environ=None):
        self.environ = environ or {}


def _prepare_auth_header(credentials):
    return {AUTH_HEADER_KEY: 'Basic %s' % credentials}


class TestAuthentication(common.TestAuthBasicCommon):
    """Test cases for basic authentication."""

    @classmethod
    def setUpClass(cls):
        """Set up data for basic authentication tests."""
        super().setUpClass()
        cls.IrHttp = cls.env['ir.http']

    def _setup_request(self, request, httprequest):
        """Patching request parts to be able to call auth method."""
        request.httprequest = httprequest
        request.env = self.env

    # Must provide spec, because patch otherwise runs
    # `if hasattr(obj, '__func__')` check which triggers call to real
    # object, which does not exist, failing mock. When spec is not none,
    # that check is skipped.
    @patch(PATCH_PATH, spec=_MockedRequest)
    def test_01_auth_method_basic(self, request):
        """Authenticate when correct credentials are passed."""
        self._setup_request(
            request,
            _MockedHttpRequest(_prepare_auth_header(self.auth_basic_1._credentials)),
        )
        res = self.IrHttp._auth_method_basic()
        self.assertEqual(res, True)
        self.assertEqual(request.uid, self.user_admin.id)
        self.assertEqual(request.auth_basic, self.auth_basic_1)
        self.assertEqual(request.auth_basic_id, self.auth_basic_1.id)

    @patch(PATCH_PATH, spec=_MockedRequest)
    def test_02_auth_method_basic(self, request):
        """Try to authenticate when incorrect credentials are passed."""
        self._setup_request(
            request, _MockedHttpRequest(_prepare_auth_header('badcredentials'))
        )
        with self.assertRaises(ValidationError):
            self.IrHttp._auth_method_basic()

    @patch(PATCH_PATH, spec=_MockedRequest)
    def test_03_auth_method_basic(self, request):
        """Try to authenticate when no credentials are passed."""
        self._setup_request(request, _MockedHttpRequest())
        with self.assertRaises(AccessDenied), mute_logger(
            'odoo.addons.auth_basic.models.ir_http'
        ):
            self.IrHttp._auth_method_basic()
