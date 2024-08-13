import responses

from odoo.tests.common import tagged

from odoo.addons.http_client.exceptions import AuthDataError, AuthError
from odoo.addons.http_client.tests.common import (
    CONTENT_TYPE_APPLICATION_JSON,
    DUMMY_BEARER_RESPONSE,
    DUMMY_ENDPOINT,
    DUMMY_URL,
)
from odoo.addons.http_client.value_objects import PathItem

from . import common


@tagged('http_client_demo_controller')
class TestHttpClientDemoController(common.TestHttpClientDemoCommon):
    """Class to test demo controller."""

    @responses.activate
    def test_01_call_http_method(self):
        """Call REST method when path_item is passed, but no auth obj."""
        # Make sure no auth obj can be found.
        (self.test_auth_1 | self.test_auth_2 | self.test_auth_3).action_to_draft()
        endpoint = DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=200, json={})
        with self.assertRaises(AuthDataError):
            self.HttpClientTestController.call_http_method(
                'get',
                options={
                    'path_item': PathItem(path_expression='my_uri/{}', args=('a',)),
                    'company_id': self.company_main.id,
                },
            )

    @responses.activate
    def test_02_call_http_method(self):
        """Call REST method when path_item is passed and is auth obj.

        Auth obj method is None.
        """
        endpoint = DUMMY_URL + '/my_uri/a'
        responses.add(responses.GET, endpoint, status=200, json={})
        response = self.HttpClientTestController.call_http_method(
            'get',
            options={
                'path_item': PathItem(path_expression='my_uri/{}', args=('a',)),
                'company_id': self.company_main.id,
            },
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test_03_call_http_method(self):
        """Call REST method when path_item is passed and is auth obj.

        Auth obj method is Basic.
        """
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={})
        response = self.HttpClientTestController.call_http_method(
            'get',
            options={
                'path_item': PathItem(path_expression='my_uri'),
                'company_id': self.company_2.id,
                'kwargs': {'headers': {'my_header': '123'}},
            },
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test_04_call_http_method(self):
        """Call REST method when auth is passed.

        Auth obj method is Basic.

        Case 1: auth not confirmed.
        Case 2: auth confirmed.
        """
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={})
        # Case 1.
        self.test_auth_2.action_to_draft()  # make it draft.
        with self.assertRaises(AuthDataError):
            self.HttpClientTestController.call_http_method(
                'get',
                options={
                    'path_item': PathItem(path_expression='my_uri'),
                    'auth': self.test_auth_2,
                    'kwargs': {'headers': {'my_header': '123'}},
                },
            )
        # Case 2.
        self.test_auth_2.action_confirm()
        response = self.HttpClientTestController.call_http_method(
            'get',
            options={
                'path_item': PathItem(path_expression='my_uri'),
                'auth': self.test_auth_2,
                'kwargs': {'headers': {'my_header': '123'}},
            },
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test_05_call_http_method(self):
        """Call REST method when Bearer/client_credentials auth is used.

        Case: OK
        """
        endpoint = DUMMY_URL + '/my_uri'
        self.test_auth_1.write(self._get_dummy_bearer_client_credentials_auth_vals())
        endpoint_auth = self.test_auth_1.path_auth
        responses.add(
            responses.POST,
            endpoint_auth,
            status=200,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            json=DUMMY_BEARER_RESPONSE,
        )
        responses.add(
            responses.GET,
            endpoint,
            headers=CONTENT_TYPE_APPLICATION_JSON,
            status=200,
            json={},
        )
        response = self.HttpClientTestController.call_http_method(
            'get',
            options={
                'path_item': PathItem(path_expression='my_uri'),
                'auth': self.test_auth_1,
                'kwargs': {'headers': {'my_header': '123'}},
            },
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    def test_06_call_http_method(self):
        """Call REST method when Bearer/client_credentials auth is used.

        Case: authentication fails.
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
            self.HttpClientTestController.call_http_method(
                'get',
                options={
                    'path_item': PathItem(path_expression='my_uri'),
                    'auth': self.test_auth_1,
                    'kwargs': {'headers': {'my_header': '123'}},
                },
            )
