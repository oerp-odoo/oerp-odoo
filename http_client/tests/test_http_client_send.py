import responses

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from ..const import HttpVerb
from ..value_objects.request import RelativePath, RequestInput
from . import common


class TestHttpClientSend(common.TestHttpClientCommon):
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
    def test_01_client_send_ok(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=200, json={})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response = self.HttpClient.send(inp)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, endpoint)

    @responses.activate
    def test_02_client_send_err(self):
        # GIVEN
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=401, json={'error': 'not-good'})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        with mute_logger('odoo.addons.http_client.model_services.http_client'):
            response = self.HttpClient.send(inp)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.request.url, endpoint)

    @responses.activate
    def test_03_client_send_err_raise(self):
        # GIVEN
        self.profile_1.non_ok_exception_path = 'odoo.exceptions.ValidationError'
        endpoint = common.DUMMY_ENDPOINT
        responses.add(responses.GET, endpoint, status=401, json={'error': 'not-good'})
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Endpoint '.+' call failed\. Method: GET, Error Code: 401, Response: .+",
        ):
            self.HttpClient.send(inp)
