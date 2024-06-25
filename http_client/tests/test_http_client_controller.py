import responses

from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from ..models.http_client_controller import get_endpoint
from . import common


@tagged('http_client_controller')
class TestHttpClientController(common.TestHttpClientCommon):
    """Class to test REST client controller."""

    def test_01_get_endpoint_no_args(self):
        """Get endpoint without args."""
        endpoint = get_endpoint('https://abc.com', '/my_pattern/a')
        self.assertEqual(endpoint, 'https://abc.com/my_pattern/a')

    def test_02_get_endpoint_with_args(self):
        """Get endpoint with args."""
        endpoint = get_endpoint(
            'https://abc.com', '/my_pattern/%s/test/%s', args=('a', 'b')
        )
        self.assertEqual(endpoint, 'https://abc.com/my_pattern/a/test/b')

    def test_03_get_endpoint_url_with_path(self):
        endpoint = get_endpoint(
            'https://abc.com/api', '/my_pattern/%s/test/%s', args=('a', 'b')
        )
        self.assertEqual(endpoint, 'https://abc.com/api/my_pattern/a/test/b')
        self.assertEqual(
            get_endpoint('https://abc.com/api', '/my_pattern/a'),
            'https://abc.com/api/my_pattern/a',
        )
        self.assertEqual(
            get_endpoint('https://abc.com/api/', '/my_pattern/a'),
            'https://abc.com/api/my_pattern/a',
        )
        self.assertEqual(
            get_endpoint('https://abc.com/', '/my_pattern/a'),
            'https://abc.com/my_pattern/a',
        )

    @responses.activate
    def test_03_call_http_method(self):
        """Call REST when response is 'ok'."""
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=200, json={})
        response = self.HttpClientController.call_http_method(
            'get', options={'endpoint': endpoint}
        )
        self.assertEqual(response.status_code, 200)

    @responses.activate
    @mute_logger(common.HTTP_CLIENT_MODULE_PATH)
    def test_04_call_http_method(self):
        """Call REST when response is 'bad_data'."""
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.POST, endpoint, status=400, json={})
        response = self.HttpClientController.call_http_method(
            'post',
            options={
                'endpoint': endpoint,
                'kwargs': {
                    'data': {'my_bad_data': 123},
                    'auth': ('user', 'passwd'),
                },
            },
        )
        self.assertEqual(response.status_code, 400)

    @responses.activate
    @mute_logger(common.HTTP_CLIENT_MODULE_PATH)
    def test_05_call_http_method(self):
        """Call REST when response is 'bad_auth'."""
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.PUT, endpoint, status=401, json={})
        response = self.HttpClientController.call_http_method(
            'put',
            options={
                'endpoint': endpoint,
                'kwargs': {
                    'data': {'my_good_data': 123},
                    'auth': ('user', 'bad_passwd'),
                },
            },
        )
        self.assertEqual(response.status_code, 401)

    @responses.activate
    @mute_logger(common.HTTP_CLIENT_MODULE_PATH)
    def test_06_call_http_method(self):
        """Call REST when response is 'bad_page'."""
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=404, json={})
        response = self.HttpClientController.call_http_method(
            'get',
            options={'endpoint': endpoint},
        )
        self.assertEqual(response.status_code, 404)

    @responses.activate
    @mute_logger(common.HTTP_CLIENT_MODULE_PATH)
    def test_07_call_http_method(self):
        """Call REST when response invalid endpoint is passed."""
        endpoint = 'invalid_endpoint'
        responses.add(responses.GET, endpoint)
        with self.assertRaises(ValidationError):
            self.HttpClientController.call_http_method(
                'get', options={'endpoint': endpoint}
            )

    def test_08_call_http_method(self):
        """Call REST when endpoint/uri_pattern is not XOR.

        Case 1: both endpoint and uri_item is used.
        Case 2: no endpoint nor uri_item is used.
        """
        # Case 1.
        endpoint = 'my_endpoint'
        uri_item = ('my_uri_pattern', False)
        with self.assertRaises(ValidationError):
            self.HttpClientController.call_http_method(
                'get', options={'endpoint': endpoint, 'uri_item': uri_item}
            )
        # Case 2.
        with self.assertRaises(ValidationError):
            self.HttpClientController.call_http_method(
                'get', options={'endpoint': False, 'uri_item': False}
            )
