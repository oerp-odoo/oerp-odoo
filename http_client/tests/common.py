import base64
import json
from datetime import datetime, timedelta

from psycopg2.extensions import AsIs
from requests.structures import CaseInsensitiveDict

from odoo.tests.common import TransactionCase


def encode_jwt_token(p1=None, p2=None, p3=None, no_padding=True):
    def encode_part(part):
        p = base64.b64encode(json.dumps(part).encode()).decode()
        # In real case scenario tokens have no padding, so we can
        # simulate that.
        if no_padding:
            p = p.replace('=', '')
        return p

    if p1 is None:
        p1 = {}
    if p2 is None:
        p2 = {}
    if p3 is None:
        p3 = {}
    p1, p2, p3 = encode_part(p1), encode_part(p2), encode_part(p3)
    r = f'{p1}.{p2}.{p3}'
    return r


MODELS_PATH = 'odoo.models'
CONTENT_TYPE_APPLICATION_JSON = CaseInsensitiveDict(
    {'Content-Type': 'application/json; charset=utf-8'}
)
# NOTE. Using local URLs, because odoo testing framework is blocking
# external URLs.
DUMMY_AUTH_TOKEN_ENDPOINT = 'https://127.0.0.1/auth/token'  # nosec: B105
# Used in bearer response.
VALID_BEARER_ACCESS_TOKEN_1 = encode_jwt_token(
    p2={
        'nbf': datetime.now().timestamp(),
        'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        'iss': DUMMY_AUTH_TOKEN_ENDPOINT,
        'client_id': 'test',
    }
)
DUMMY_BEARER_RESPONSE = {
    'access_token': VALID_BEARER_ACCESS_TOKEN_1,
    'expires_in': 3600,
    'token_type': 'Bearer',
    'scope': 'some/scope',
}
DUMMY_URL = 'http://127.0.0.1'
DUMMY_PATH = '/my_path'
DUMMY_ENDPOINT = f"{DUMMY_URL}{DUMMY_PATH}"
HTTP_CLIENT_MODULE_PATH = 'odoo.addons.http_client.models.http_client_controller'
# Tokens with expiration.
VALID_ACCESS_TOKEN_1 = encode_jwt_token(
    p2={
        'token_type': 'access',
        'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        'jti': 'blabla123',
        'user_id': 555,
    }
)
VALID_REFRESH_TOKEN_1 = encode_jwt_token(
    p2={
        'token_type': 'refresh',
        # Normally refresh token duration should be longer
        # than access token.
        'exp': (datetime.now() + timedelta(days=2)).timestamp(),
        'jti': 'blabla123',
        'user_id': 555,
    }
)


class TestHttpClientCommon(TransactionCase):
    """Common class for HTTP client tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data."""
        super().setUpClass()
        cls.company_main = cls.env.ref('base.main_company')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.group_user = cls.env.ref('base.group_user')
        cls.HttpClient = cls.env['http.client']
        cls.HttpClientRetry = cls.env['http.client.retry']
        cls.HttpClientAuth = cls.env['http.client.auth']
        cls.HttpClientEncoder = cls.env['http.client.encoder']
        cls.HttpClientProfile = cls.env['http.client.profile']
        cls.HttpClientTransport = cls.env['http.client.transport']

    @classmethod
    def get_auth_model(cls):
        raise NotImplementedError()

    @classmethod
    def create_auth(cls, vals=None):
        if not vals:
            vals = {}
        vals.setdefault('url', DUMMY_URL)
        return cls.get_auth_model().create(vals)

    @classmethod
    def _get_dummy_bearer_client_credentials_auth_vals(cls):
        return {
            'auth_method': 'bearer',
            'identifier': 'clientID',
            'secret': 'ClientSecret',
            'grant_type': 'client_credentials',
            'scope': 'some/scope',
            'auth_path_type': 'endpoint',
            'path_auth': DUMMY_AUTH_TOKEN_ENDPOINT,
            'content_type': 'x-www-form-urlencoded',
        }

    @classmethod
    def _get_dummy_jwt_password_auth_vals(cls):
        return {
            'auth_method': 'jwt',
            'identifier': 'clientID',
            'secret': 'ClientSecret',
            'grant_type': 'password',
            'auth_path_type': 'path',
            'refresh_path_type': 'path',
            'path_auth': '/auth/token/',
            # To also use token refresh.
            'path_refresh': '/auth/refresh/',
            'content_type': 'json',
        }

    @classmethod
    def _get_dummy_jwt_verify_vals(cls):
        return {
            'auth_method': 'jwt',
            'identifier': 'clientID',
            'secret': 'ClientSecret',
            'grant_type': 'password',
            'verify_path_type': 'path',
            'path_verify': '/auth/token/verify/',
        }

    @classmethod
    def _get_dummy_api_key_credentials(cls):
        return {
            'auth_method': 'api_key',
            'identifier': 'ApiKey',
            'secret': 'SECRET_API_KEY',
        }

    @classmethod
    def _update_create_date(cls, records, dt):
        table = records._table
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        cls.env.cr.execute(
            """
            UPDATE %s
            SET create_date = %s
            WHERE id in %s
            """,
            (AsIs(table), dt_str, tuple(records.ids)),
        )

    def mock_jwt_access_ok(self, auth, respones_):
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        auth.write(vals)
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        respones_.add(
            respones_.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
                'user': {},
            },
        )
        return endpoint_auth
