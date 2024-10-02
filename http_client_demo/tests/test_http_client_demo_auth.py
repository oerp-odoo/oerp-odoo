from datetime import datetime, timedelta

import responses

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from odoo.addons.http_client.exceptions import AuthError
from odoo.addons.http_client.tests.common import (
    CONTENT_TYPE_APPLICATION_JSON,
    DUMMY_AUTH_TOKEN_ENDPOINT,
    DUMMY_BEARER_RESPONSE,
    DUMMY_URL,
    HTTP_CLIENT_MODULE_PATH,
    MODELS_PATH,
    VALID_ACCESS_TOKEN_1,
    VALID_BEARER_ACCESS_TOKEN_1,
    VALID_REFRESH_TOKEN_1,
    encode_jwt_token,
)

from . import common

EXPIRED_BEARER_ACCESS_TOKEN_1 = encode_jwt_token(
    p2={
        'nbf': 1640000000,
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'iss': DUMMY_AUTH_TOKEN_ENDPOINT,
        'client_id': 'test',
    }
)
EXPIRED_ACCESS_TOKEN_1 = encode_jwt_token(
    p2={
        'token_type': 'access',
        # Expiration time.
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'jti': 'blabla123',
        'user_id': 555,
    }
)
EXPIRED_REFRESH_TOKEN_1 = encode_jwt_token(
    p2={
        'token_type': 'refresh',
        'exp': 1640988000,  # 2022-01-01 00:00:00
        'jti': 'blabla123',
        'user_id': 555,
    }
)
VALID_ACCESS_TOKEN_2 = encode_jwt_token(
    p2={
        'token_type': 'access',
        'exp': (datetime.now() + timedelta(days=10)).timestamp(),
        'jti': 'blabla333',
        'user_id': 666,
    }
)
VALID_REFRESH_TOKEN_2 = encode_jwt_token(
    p2={
        'token_type': 'refresh',
        'exp': (datetime.now() + timedelta(days=20)).timestamp(),
        'jti': 'blabla4654',
        'user_id': 666,
    }
)


@tagged('http_client_demo_auth')
class TestHttpClientDemoAuth(common.TestHttpClientDemoCommon):
    """Class to test demo authentication."""

    def test_01_get_auth(self):
        """Get current auth when no auth is confirmed.

        Case 1: main company.
        Case 2: second company.
        """
        # Case 1.
        (self.test_auth_1 | self.test_auth_2 | self.test_auth_3).action_to_draft()
        self.assertEqual(self.test_auth_1.state, 'draft')
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_main.id)
        self.assertEqual(auth, self.HttpClientTestAuth)
        # Case 2.
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_2.id)
        self.assertEqual(auth, self.HttpClientTestAuth)

    def test_02_get_auth(self):
        """Get current auth per company.

        Case 1: main company.
        Case 2: second company.
        Case 3: no company (global).
        """
        # Case 1.
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_main.id)
        self.assertEqual(auth, self.test_auth_1)
        # Case 2.
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_2.id)
        self.assertEqual(auth, self.test_auth_2)
        # Case 3.
        # Disable company specific auth record, so it would default
        # to global one.
        self.test_auth_1.action_to_draft()
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_main.id)
        self.assertEqual(auth, self.test_auth_3)
        # Sanity check, to make sure, global defaults to only those
        # auth that have no specific company.
        auth = self.HttpClientTestAuth.get_auth(company_id=self.company_2.id)
        self.assertEqual(auth, self.test_auth_2)

    def test_03_auth_access_rights_non_admin(self):
        # GIVEN
        auth = self.HttpClientTestAuth.with_user(self.user_demo)
        # WHEN, THEN
        with self.assertRaises(AccessError):
            auth.check_access_rights('read')
        with self.assertRaises(AccessError):
            auth.check_access_rights('write')
        with self.assertRaises(AccessError):
            auth.check_access_rights('create')
        with self.assertRaises(AccessError):
            auth.check_access_rights('unlink')

    def test_04_auth_access_rights_admin(self):
        # GIVEN
        auth = self.HttpClientTestAuth.with_user(self.user_admin)
        # WHEN, THEN
        try:
            auth.check_access_rights('read')
            auth.check_access_rights('write')
            auth.check_access_rights('create')
            auth.check_access_rights('unlink')
        except AccessError as e:
            self.fail(f"Access rights error must have not been raised. Error: {e}")

    def test_05_auth_access_rules_company_matches_user_company(self):
        # GIVEN
        auth = self.test_auth_1.with_user(self.user_demo)
        # WHEN, THEN
        try:
            auth.check_access_rule('read')
            auth.check_access_rule('write')
            auth.check_access_rule('create')
            auth.check_access_rule('unlink')
        except AccessError as e:
            self.fail(f"Access rule error must have not been raised. Error: {e}")

    def test_06_auth_access_rules_company_not_match_user_company(self):
        # GIVEN
        auth = self.test_auth_2.with_user(self.user_demo)
        # WHEN, THEN
        with self.assertRaises(AccessError):
            auth.check_access_rule('read')
        with self.assertRaises(AccessError):
            auth.check_access_rule('write')
        with self.assertRaises(AccessError):
            auth.check_access_rule('create')
        with self.assertRaises(AccessError):
            auth.check_access_rule('unlink')

    def test_07_auth_access_rules_no_company_set(self):
        # GIVEN
        auth = self.test_auth_3.with_user(self.user_demo)
        # WHEN, THEN
        try:
            auth.check_access_rule('read')
            auth.check_access_rule('write')
            auth.check_access_rule('create')
            auth.check_access_rule('unlink')
        except AccessError as e:
            self.fail(f"Access rule error must have not been raised. Error: {e}")

    def test_08_get_auth_data(self):
        """Try to get auth data from model that has no auth model."""
        data = self.env['http.client.controller']._get_auth_data(self.company_main.id)
        self.assertEqual(data, None)

    def test_09_get_auth_data(self):
        """Try to get auth data with user that has no access."""
        with self.assertRaises(AccessError), mute_logger(MODELS_PATH):
            self.HttpClientTestController.with_user(self.user_demo)._get_auth_data(
                self.company_main.id
            )

    def test_10_get_auth_data(self):
        """Get auth data with None auth method."""
        data = self.HttpClientTestController._get_auth_data(self.company_main.id)
        self.assertEqual(data, {'url': self.test_auth_1.url, 'auth': None})

    def test_11_get_auth_data(self):
        """Get auth data with Basic auth method."""
        data = self.HttpClientTestController._get_auth_data(self.company_2.id)
        auth = self.test_auth_2
        self.assertEqual(
            data,
            {
                'url': auth.url,
                'auth': {'auth': (auth.identifier, auth.secret)},
            },
        )

    def test_12_token_expire_delta_higher_than_zero(self):
        with self.assertRaisesRegex(
            ValidationError, r"Token Expire Delta must be 0 or lower!"
        ):
            self.test_auth_1.token_expire_delta = 100

    @responses.activate
    def test_13_get_auth_data_bearer_w_endpoint_init_token(self):
        # GIVEN
        self.test_auth_1.write(self._get_dummy_bearer_client_credentials_auth_vals())
        endpoint_auth = self.test_auth_1.path_auth
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json=DUMMY_BEARER_RESPONSE,
        )
        # WHEN
        data = self.test_auth_1.get_data()
        # THEN
        responses.assert_call_count(endpoint_auth, 1)
        self.assertEqual(
            data,
            {
                'url': self.test_auth_1.url,
                'auth': {
                    'headers': {
                        'Authorization': 'Bearer %s' % VALID_BEARER_ACCESS_TOKEN_1
                    }
                },
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)
        # Should return same thing.
        data = self.test_auth_1.get_data()
        self.assertEqual(
            data,
            {
                'url': self.test_auth_1.url,
                'auth': {
                    'headers': {
                        'Authorization': 'Bearer %s' % VALID_BEARER_ACCESS_TOKEN_1
                    }
                },
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)
        # Should not request auth again as we are reusing saved token.
        responses.assert_call_count(endpoint_auth, 1)

    @responses.activate
    def test_14_get_auth_data_bearer_w_endpoint_replace_expired_token(self):
        # GIVEN
        self.test_auth_1.write(
            dict(
                self._get_dummy_bearer_client_credentials_auth_vals(),
                access_token=EXPIRED_BEARER_ACCESS_TOKEN_1,
            )
        )
        endpoint_auth = self.test_auth_1.path_auth
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json=DUMMY_BEARER_RESPONSE,
        )
        # WHEN
        data = self.test_auth_1.get_data()
        # THEN
        responses.assert_call_count(endpoint_auth, 1)
        self.assertEqual(
            data,
            {
                'url': self.test_auth_1.url,
                'auth': {
                    'headers': {
                        'Authorization': 'Bearer %s' % VALID_BEARER_ACCESS_TOKEN_1
                    }
                },
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)
        # Should return same thing.
        data = self.test_auth_1.get_data()
        self.assertEqual(
            data,
            {
                'url': self.test_auth_1.url,
                'auth': {
                    'headers': {
                        'Authorization': 'Bearer %s' % VALID_BEARER_ACCESS_TOKEN_1
                    }
                },
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_BEARER_ACCESS_TOKEN_1)
        # Should not request auth again as we are reusing saved token.
        responses.assert_call_count(endpoint_auth, 1)

    @responses.activate
    def test_15_get_auth_data_bearer_w_endpoint_token_expired_by_delta(self):
        # GIVEN
        # Setting valid token in current time, but not valid by expire
        # delta!
        self.test_auth_1.write(
            dict(
                self._get_dummy_bearer_client_credentials_auth_vals(),
                access_token=VALID_BEARER_ACCESS_TOKEN_1,
                token_expire_delta=-1000000,
            )
        )
        endpoint_auth = self.test_auth_1.path_auth
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json=DUMMY_BEARER_RESPONSE,
        )
        # WHEN
        self.test_auth_1.get_data()
        # THEN
        # Must call auth, to get new token.
        responses.assert_call_count(endpoint_auth, 1)

    @responses.activate
    def test_16_get_auth_data_bearer_w_path_init_token(self):
        path_auth = '/auth/token'
        self.test_auth_1.write(
            dict(
                self._get_dummy_bearer_client_credentials_auth_vals(),
                auth_path_type='path',
                path_auth=path_auth,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json=DUMMY_BEARER_RESPONSE,
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {
                    'headers': {
                        'Authorization': f'Bearer {VALID_BEARER_ACCESS_TOKEN_1}'
                    }
                },
            },
        )

    @responses.activate
    @mute_logger(HTTP_CLIENT_MODULE_PATH)
    def test_17_get_auth_data_bearer(self):
        """Try to get Bearer auth with incorrect credentials.

        Case: response returns 400 error code.
        """
        self.test_auth_1.write(self._get_dummy_bearer_client_credentials_auth_vals())
        endpoint_auth = self.test_auth_1.path_auth
        responses.add(
            responses.POST,
            endpoint_auth,
            status=400,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={'error': 'invalid_client'},
        )
        with self.assertRaises(AuthError):
            self.HttpClientTestController._get_auth_data(self.company_main.id)

    @responses.activate
    def test_18_jwt_n_password_init_token(self):
        """Get JWT token initially."""
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        self.test_auth_1.write(vals)
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
                'user': {},
            },
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'}},
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_1)

    @responses.activate
    def test_19_jwt_n_password_refresh_token_expired_reusable(self):
        """Refresh JWT token having expired access token.

        Case: refresh token is reusable
        """
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        path_refresh = vals['path_refresh']
        # Save with expired access token to get it refreshed.
        self.test_auth_1.write(
            dict(
                vals,
                access_token=EXPIRED_ACCESS_TOKEN_1,
                refresh_token=VALID_REFRESH_TOKEN_1,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        # Generate not expired tokens, to trigger refresh.
        endpoint_refresh = f'{DUMMY_URL}{path_refresh}'
        responses.add(
            responses.POST,
            endpoint_refresh,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access': VALID_ACCESS_TOKEN_1,
                'access_token_expiration': 'blabla',
            },
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'}},
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_1)
        self.assertTrue(responses.assert_call_count(endpoint_auth, 0))
        self.assertTrue(responses.assert_call_count(endpoint_refresh, 1))

    @responses.activate
    def test_20_jwt_n_password_refresh_token_expired_not_reusable(self):
        """Refresh JWT token having expired access token.

        Case: refresh token can be used only once.
        """
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        path_refresh = vals['path_refresh']
        # Save with expired access token to get it refreshed.
        self.test_auth_1.write(
            dict(
                vals,
                access_token=EXPIRED_ACCESS_TOKEN_1,
                refresh_token=VALID_REFRESH_TOKEN_1,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        endpoint_refresh = f'{DUMMY_URL}{path_refresh}'
        responses.add(
            responses.POST,
            endpoint_refresh,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access': VALID_ACCESS_TOKEN_1,
                'refresh': VALID_REFRESH_TOKEN_2,
            },
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'}},
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_2)
        self.assertTrue(responses.assert_call_count(endpoint_auth, 0))
        self.assertTrue(responses.assert_call_count(endpoint_refresh, 1))

    @responses.activate
    def test_21_jwt_n_password_refresh_token_revoked_relogin(self):
        """Re-login on refresh token being invalid, but not expired."""
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        path_refresh = vals['path_refresh']
        self.test_auth_1.write(
            dict(
                vals,
                access_token=EXPIRED_ACCESS_TOKEN_1,
                # Here token is valid, that its not expired, but in
                # this case, it was blacklisted, so remote will not
                # accept it!
                refresh_token=VALID_REFRESH_TOKEN_1,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        endpoint_refresh = f'{DUMMY_URL}{path_refresh}'
        responses.add(
            responses.POST,
            endpoint_refresh,
            status=401,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={'msg': 'Refresh token has been blacklisted'},
        )
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_2,
                'refresh_token': VALID_REFRESH_TOKEN_2,
                'user': {},
            },
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'Authorization': f'JWT {VALID_ACCESS_TOKEN_2}'}},
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_2)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_2)
        self.assertTrue(responses.assert_call_count(endpoint_refresh, 1))
        self.assertTrue(responses.assert_call_count(endpoint_auth, 1))

    @responses.activate
    def test_22_jwt_n_password_reinit_token(self):
        """Get new tokens when both access and refresh expired."""
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        # Both tokens expired, to trigger new token request.
        self.test_auth_1.write(
            dict(
                vals,
                access_token=EXPIRED_ACCESS_TOKEN_1,
                refresh_token=EXPIRED_REFRESH_TOKEN_1,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
                'user': {},
            },
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'Authorization': f'JWT {VALID_ACCESS_TOKEN_1}'}},
            },
        )
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_1)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_1)

    def test_23_get_auth_data(self):
        """Get auth data by explicitly passing auth record."""
        data = self.HttpClientTestController._get_auth_data(
            self.company_main.id, auth=self.test_auth_2
        )
        auth = self.test_auth_2
        self.assertEqual(
            data,
            {
                'url': auth.url,
                'auth': {'auth': (auth.identifier, auth.secret)},
            },
        )

    def test_24_get_token_secret(self):
        """Generate token from secret field."""
        token = self.test_auth_2.provide_token()
        self.assertEqual(token, self.test_auth_2.secret)

    def test_25_check_auth_unique(self):
        """Enable auth records, when uniqueness is not satisfied.

        Case 1: dupe company.
        Case 2: dupe global auth.
        """
        # Case 1.
        auth = self.create_auth()
        with self.assertRaises(ValidationError):
            auth.action_confirm()
        # Case 2.
        auth = self.create_auth({'company_id': False})
        with self.assertRaises(ValidationError):
            auth.action_confirm()

    def test_26_check_path_auth(self):
        """Try to set invalid URL for Authentication endpoint."""
        with self.assertRaises(ValidationError):
            self.test_auth_1.write(
                dict(
                    self._get_dummy_bearer_client_credentials_auth_vals(),
                    path_auth='some_incorrect_url',
                )
            )

    @responses.activate
    def test_27_action_login_get_new_token(self):
        """Force request new tokens replacing valid ones."""
        vals = self._get_dummy_jwt_password_auth_vals()
        path_auth = vals['path_auth']
        # Saving valid ones to make sure these are forced replaced.
        self.test_auth_1.write(
            dict(
                vals,
                access_token=VALID_ACCESS_TOKEN_1,
                refresh_token=VALID_REFRESH_TOKEN_1,
            )
        )
        endpoint_auth = f'{DUMMY_URL}{path_auth}'
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={
                'access_token': VALID_ACCESS_TOKEN_2,
                'refresh_token': VALID_REFRESH_TOKEN_2,
                'user': {},
            },
        )
        self.test_auth_1.action_login()
        self.assertEqual(self.test_auth_1.access_token, VALID_ACCESS_TOKEN_2)
        self.assertEqual(self.test_auth_1.refresh_token, VALID_REFRESH_TOKEN_2)

    @responses.activate
    def test_28_action_verify_ok(self):
        vals = self._get_dummy_jwt_verify_vals()
        path_verify = vals['path_verify']
        # Saving valid ones to make sure these are forced replaced.
        self.test_auth_1.write(
            dict(
                vals,
                access_token=VALID_ACCESS_TOKEN_1,
                refresh_token=VALID_REFRESH_TOKEN_1,
            )
        )
        endpoint_verify = f'{DUMMY_URL}{path_verify}'
        responses.add(
            responses.POST,
            endpoint_verify,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json={},
        )
        self.test_auth_1.action_verify()
        self.assertTrue(responses.assert_call_count(endpoint_verify, 1))

    def test_29_action_logout(self):
        self.test_auth_1.write(
            {
                'access_token': VALID_ACCESS_TOKEN_1,
                'refresh_token': VALID_REFRESH_TOKEN_1,
            }
        )
        self.test_auth_1.action_logout()
        self.assertFalse(self.test_auth_1.access_token)
        self.assertFalse(self.test_auth_1.refresh_token)

    def test_30_api_key_auth(self):
        self.test_auth_1.write(self._get_dummy_api_key_credentials())
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'ApiKey': 'SECRET_API_KEY'}},
            },
        )

    def test_31_api_key_auth_custom_identifier(self):
        self.test_auth_1.write(
            dict(self._get_dummy_api_key_credentials(), identifier='X-API-KEY')
        )
        self.assertEqual(
            self.test_auth_1.get_data(),
            {
                'url': self.test_auth_1.url,
                'auth': {'headers': {'X-API-KEY': 'SECRET_API_KEY'}},
            },
        )
