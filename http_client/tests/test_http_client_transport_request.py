import json

import requests
import responses

from odoo.exceptions import ValidationError

from ..const import FORMAT_JSON, HttpVerb
from ..value_objects.request import RelativePath, RequestInput
from . import common


class TestHttpClientTransportRequest(common.TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )
        cls.auth_1.action_confirm()
        cls.profile_1 = cls.HttpClientProfile.create(
            {
                'name': 'MY-PROFILE-1',
                'base_url': common.DUMMY_URL,
                'auth_id': cls.auth_1.id,
            }
        )

    @responses.activate
    def test_01_transport_request_ok(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=200, json={})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
            headers={'CUSTOM-HEADER-1': 'ABC'},
        )
        # WHEN
        response = self.HttpClientTransport.request(inp)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.headers['CUSTOM-HEADER-1'], 'ABC')
        self.assertEqual(response.request.url, endpoint)

    @responses.activate
    def test_02_transport_request_profile_inactive(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        self.profile_1.active = False
        responses.add(responses.GET, endpoint, status=200, json={})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        with self.assertRaisesRegex(
            ValidationError, r"HTTP Client Profile \(.+\) is inactive!"
        ):
            self.HttpClientTransport.request(inp)

    @responses.activate
    def test_03_transport_request_err(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=401, json={'error': 'not-good'})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response = self.HttpClientTransport.request(inp)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.request.url, endpoint)

    @responses.activate
    def test_04_transport_request_w_json_data_ok(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.POST, endpoint, status=200, json={})
        inp = RequestInput(
            method=HttpVerb.POST,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
            headers={'Content-Type': 'application/json'},
            data_format_type=FORMAT_JSON,
            data={'x': 10},
        )
        # WHEN
        response = self.HttpClientTransport.request(inp)
        self.assertEqual(response.status_code, 200)
        request = response.request
        self.assertEqual(json.loads(request.body.decode()), {'x': 10})
        self.assertEqual(request.headers['Content-Type'], 'application/json')
        self.assertEqual(request.url, endpoint)

    @responses.activate
    def test_05_transport_request_w_basic_auth_ok(self):
        # GIVEN
        self.auth_1.write(
            {
                'auth_method': 'basic',
                'identifier': 'my-user-1',
                'secret': 'my-password-1',
            }
        )
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=200, json={})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response = self.HttpClientTransport.request(inp)
        self.assertEqual(response.status_code, 200)
        request = response.request
        self.assertEqual(
            request.headers['Authorization'], 'Basic bXktdXNlci0xOm15LXBhc3N3b3JkLTE='
        )
        self.assertEqual(request.url, endpoint)

    @responses.activate(registry=responses.registries.OrderedRegistry)
    def test_06_transport_request_retry_ok(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'retries_total': 4,
                'backoff_factor': 0,
                'allowed_methods': 'GET,POST',
                'status_forcelist': '500',
                'mount_prefixes': 'http://',
            }
        )
        self.profile_1.retry_id = retry.id
        endpoint = common.DUMMY_ENDPOINT
        inp = RequestInput(
            method=HttpVerb.GET,
            url=endpoint,
            profile=self.profile_1,
        )
        resp1 = responses.get(
            endpoint, status=500, json={'error': 'something-went-wrong'}
        )
        resp2 = responses.get(endpoint, status=200, json={})
        # WHEN
        response = self.HttpClientTransport.request(inp)
        # THEN
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(resp1.status, 500)
        self.assertEqual(resp2.status, 200)
        self.assertEqual(response.status_code, 200)

    @responses.activate(registry=responses.registries.OrderedRegistry)
    def test_07_transport_request_retry_exhausted(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'retries_total': 1,
                'backoff_factor': 0,
                'allowed_methods': 'GET,POST',
                'status_forcelist': '500',
                'mount_prefixes': 'http://',
            }
        )
        self.profile_1.retry_id = retry.id
        endpoint = common.DUMMY_ENDPOINT
        inp = RequestInput(
            method=HttpVerb.GET,
            url=endpoint,
            profile=self.profile_1,
        )
        responses.get(endpoint, status=500, json={'error': 'something-went-wrong'})
        responses.get(endpoint, status=500, json={'error': 'something-went-wrong'})
        responses.get(endpoint, status=200, json={})
        # WHEN, THEN
        with self.assertRaisesRegex(
            requests.exceptions.RetryError, r"Max retries exceeded with url"
        ):
            self.HttpClientTransport.request(inp)

    @responses.activate(registry=responses.registries.OrderedRegistry)
    def test_08_transport_request_retry_exhausted_not_raise(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'retries_total': 1,
                'backoff_factor': 0,
                'allowed_methods': 'GET,POST',
                'status_forcelist': '500',
                'mount_prefixes': 'http://',
                'raise_on_status': False,
            }
        )
        self.profile_1.retry_id = retry.id
        endpoint = common.DUMMY_ENDPOINT
        inp = RequestInput(
            method=HttpVerb.GET,
            url=endpoint,
            profile=self.profile_1,
        )
        responses.get(endpoint, status=500, json={'error': 'something-went-wrong'})
        responses.get(endpoint, status=500, json={'error': 'something-went-wrong'})
        responses.get(endpoint, status=200, json={})
        # WHEN
        response = self.HttpClientTransport.request(inp)
        # THEN
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"error": "something-went-wrong"})
