from datetime import datetime, timedelta

import responses

from ..exceptions import AuthError
from . import common

AUTH_BASE_URL = 'http://127.0.0.1'
PATH_AUTH = '/auth/token'
PATH_REFRESH = '/auth/refresh'
PATH_VERIFY = '/auth/token/verify'
URL_AUTH = f'{AUTH_BASE_URL}{PATH_AUTH}'
URL_REFRESH = f'{AUTH_BASE_URL}{PATH_REFRESH}'
URL_VERIFY = f'{AUTH_BASE_URL}{PATH_VERIFY}'


VALID_BEARER_ACCESS_TOKEN_1 = common.encode_jwt_token(
    p2={
        'nbf': datetime.now().timestamp(),
        'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        'iss': URL_AUTH,
        'client_id': 'test',
    }
)
VALID_BEARER_ACCESS_TOKEN_2 = common.encode_jwt_token(
    p2={
        'nbf': datetime.now().timestamp(),
        'exp': (datetime.now() + timedelta(days=2)).timestamp(),
        'iss': URL_AUTH,
        'client_id': 'test',
    }
)
BEARER_RESPONSE_1 = {
    'access_token': VALID_BEARER_ACCESS_TOKEN_1,
    'expires_in': 3600,
    'token_type': 'Bearer',
    'scope': 'some/scope',
}
BEARER_RESPONSE_2 = {
    'access_token': VALID_BEARER_ACCESS_TOKEN_2,
    'expires_in': 3600,
    'token_type': 'Bearer',
    'scope': 'some/scope',
}
EXPIRED_BEARER_ACCESS_TOKEN_1 = common.encode_jwt_token(
    p2={
        'nbf': 1640000000,
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'iss': URL_AUTH,
        'client_id': 'test',
    }
)
EXPIRED_ACCESS_TOKEN_1 = common.encode_jwt_token(
    p2={
        'token_type': 'access',
        # Expiration time.
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'jti': 'blabla123',
        'user_id': 555,
    }
)
EXPIRED_REFRESH_TOKEN_1 = common.encode_jwt_token(
    p2={
        'token_type': 'refresh',
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'jti': 'blabla123',
        'user_id': 555,
    }
)

# Tokens with expiration.
VALID_ACCESS_TOKEN_1 = common.encode_jwt_token(
    p2={
        'token_type': 'access',
        'exp': (datetime.now() + timedelta(days=1)).timestamp(),
        'jti': 'blabla123',
        'user_id': 555,
    }
)
VALID_ACCESS_TOKEN_2 = common.encode_jwt_token(
    p2={
        'token_type': 'access',
        'exp': (datetime.now() + timedelta(days=10)).timestamp(),
        'jti': 'blabla333',
        'user_id': 666,
    }
)
VALID_REFRESH_TOKEN_1 = common.encode_jwt_token(
    p2={
        'token_type': 'refresh',
        # Normally refresh token duration should be longer
        # than access token.
        'exp': (datetime.now() + timedelta(days=2)).timestamp(),
        'jti': 'blabla123',
        'user_id': 555,
    }
)
VALID_REFRESH_TOKEN_2 = common.encode_jwt_token(
    p2={
        'token_type': 'refresh',
        'exp': (datetime.now() + timedelta(days=20)).timestamp(),
        'jti': 'blabla4654',
        'user_id': 666,
    }
)


class TestHttpClientAuthAuthorize(common.TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )
        cls.auth_1.action_confirm()

    def test_01_authorize_none(self):
        self.assertEqual(self.auth_1.authorize(), {})

    def test_02_authorize_basic(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'basic',
                'identifier': 'my-user-1',
                'secret': 'my-password-1',
            }
        )
        self.assertEqual(
            self.auth_1.authorize(),
            {'Authorization': 'Basic bXktdXNlci0xOm15LXBhc3N3b3JkLTE='},
        )

    def test_03_authorize_key(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'api_key',
                'identifier': 'ApiKey',
                'secret': 'SECRET_API_KEY',
            }
        )
        # WHEN
        res = self.auth_1.authorize()
        # THEN
        self.assertEqual(res, {'ApiKey': 'SECRET_API_KEY'})

    def test_04_authorize_key_custom(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'api_key',
                'identifier': 'X-API-KEY',
                'secret': 'SECRET_API_KEY',
            }
        )
        # WHEN
        res = self.auth_1.authorize()
        # THEN
        self.assertEqual(res, {'X-API-KEY': 'SECRET_API_KEY'})

    @responses.activate
    def test_05_authorize_bearer_init(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'bearer',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'client_credentials',
                'scope': 'some/scope',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'content_type': 'x-www-form-urlencoded',
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json=BEARER_RESPONSE_1,
        )
        # WHEN
        res = self.auth_1.authorize()
        res_2 = self.auth_1.authorize()
        # THEN
        # Should be called only once as access_token should be saved
        # and reused.
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(
            res, {'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_1}'}
        )
        self.assertEqual(
            res_2, {'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_1}'}
        )
        self.assertEqual(self.auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)

    @responses.activate
    def test_06_authorize_bearer_update_expired(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'bearer',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'client_credentials',
                'scope': 'some/scope',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'content_type': 'x-www-form-urlencoded',
                'access_token': EXPIRED_BEARER_ACCESS_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json=BEARER_RESPONSE_1,
        )
        # WHEN
        res = self.auth_1.authorize()
        res_2 = self.auth_1.authorize()
        # THEN
        # Should be called only once as access_token should be saved
        # and reused.
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(
            res, {'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_1}'}
        )
        self.assertEqual(
            res_2, {'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_1}'}
        )
        self.assertEqual(self.auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)

    @responses.activate
    def test_07_authorize_bearer_update_expired_by_delta(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'bearer',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'client_credentials',
                'scope': 'some/scope',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'content_type': 'x-www-form-urlencoded',
                # Setting valid token in current time, but not valid by expire
                # delta!
                'access_token': VALID_BEARER_ACCESS_TOKEN_1,
                'token_expire_delta': -1000000,
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json=BEARER_RESPONSE_2,
        )
        # WHEN
        res = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(
            res, {'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_2}'}
        )
        self.assertEqual(self.auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_2)

    @responses.activate
    def test_08_authorize_bearer_incorrect_creds(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'bearer',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'client_credentials',
                'scope': 'some/scope',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'content_type': 'x-www-form-urlencoded',
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=400,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={'error': 'invalid_client'},
        )
        # WHEN, THEN
        with self.assertRaises(AuthError):
            self.auth_1.authorize()

    @responses.activate
    def test_09_authorize_jwt_init(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
                'user': {},
            },
        )
        # WHEN
        res = self.auth_1.authorize()
        res_2 = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_AUTH, 1)
        responses.assert_call_count(URL_REFRESH, 0)
        self.assertEqual(res, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(res_2, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_1)

    @responses.activate
    def test_10_authorize_jwt_access_expired_refresh_token_valid(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
                'access_token': EXPIRED_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_REFRESH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access': VALID_ACCESS_TOKEN_1,
                'access_token_expiration': 'blabla',
            },
        )
        # WHEN
        res = self.auth_1.authorize()
        res_2 = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_AUTH, 0)
        responses.assert_call_count(URL_REFRESH, 1)
        self.assertEqual(res, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(res_2, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_1)

    @responses.activate
    def test_11_authorize_jwt_access_expired_refresh_token_cant_be_reused(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
                'access_token': EXPIRED_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_REFRESH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access': VALID_ACCESS_TOKEN_1,
                'refresh': VALID_REFRESH_TOKEN_2,
            },
        )
        # WHEN
        res = self.auth_1.authorize()
        res_2 = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_AUTH, 0)
        responses.assert_call_count(URL_REFRESH, 1)
        self.assertEqual(res, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(res_2, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'})
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_2)

    @responses.activate
    def test_12_authorize_jwt_refresh_token_revoked(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
                'access_token': EXPIRED_ACCESS_TOKEN_1,
                # Here token is valid, that its not expired, but in
                # this case, it was blacklisted, so remote will not
                # accept it!
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_REFRESH,
            status=400,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={'msg': 'Refresh token has been blacklisted'},
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_2,
                'refresh_token': VALID_REFRESH_TOKEN_2,
                'user': {},
            },
        )
        # WHEN
        res = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_REFRESH, 1)
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(res, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_2}'})
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_2)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_2)

    @responses.activate
    def test_13_authorize_jwt_access_n_refresh_expired(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
                'access_token': EXPIRED_ACCESS_TOKEN_1,
                'refresh_token': EXPIRED_REFRESH_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_2,
                'refresh_token': VALID_REFRESH_TOKEN_2,
                'user': {},
            },
        )
        # WHEN
        res = self.auth_1.authorize()
        # THEN
        responses.assert_call_count(URL_REFRESH, 0)
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(res, {'Authorization': f'JWT {VALID_ACCESS_TOKEN_2}'})
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_2)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_2)

    @responses.activate
    def test_14_authorize_jwt_relogin(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_auth': PATH_AUTH,
                'path_refresh': PATH_REFRESH,
                'content_type': 'json',
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_AUTH,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_2,
                'refresh_token': VALID_REFRESH_TOKEN_2,
                'user': {},
            },
        )
        # WHEN
        self.auth_1.action_login()
        # THEN
        responses.assert_call_count(URL_REFRESH, 0)
        responses.assert_call_count(URL_AUTH, 1)
        self.assertEqual(self.auth_1.access_token, VALID_ACCESS_TOKEN_2)
        self.assertEqual(self.auth_1.refresh_token, VALID_REFRESH_TOKEN_2)

    @responses.activate
    def test_15_authorize_jwt_verify(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'jwt',
                'identifier': 'clientID',
                'secret': 'ClientSecret',
                'grant_type': 'password',
                'base_url': AUTH_BASE_URL,
                'path_verify': PATH_VERIFY,
                'access_token': VALID_ACCESS_TOKEN_1,
            }
        )
        responses.add(
            responses.POST,
            URL_VERIFY,
            status=200,
            headers=common.CONTENT_TYPE_APPLICATION_JSON,
            json={},
        )
        # WHEN
        self.auth_1.action_verify()
        # THEN
        responses.assert_call_count(URL_VERIFY, 1)

    def test_16_auth_action_logout(self):
        # GIVEN
        self.auth_1.write(
            {
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        # WHEN
        self.auth_1.action_logout()
        # THEN
        self.assertFalse(self.auth_1.access_token)
        self.assertFalse(self.auth_1.refresh_token)
