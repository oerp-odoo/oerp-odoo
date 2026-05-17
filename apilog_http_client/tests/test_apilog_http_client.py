import json

import responses

from odoo.tools import mute_logger

from odoo.addons.apilog.tests.common import TestApilogCommon
from odoo.addons.apilog.value_objects import RequestDirection
from odoo.addons.http_client.const import FORMAT_JSON
from odoo.addons.http_client.tests.common import DUMMY_URL, TestHttpClientCommon
from odoo.addons.http_client.value_objects.request import RequestInput


class TestApilogHttpClient(TestApilogCommon, TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.apilog_config_1 = cls.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': RequestDirection.OUTGOING,
                'source': 'http_client',
                'match_expression': 'True',
                'active': True,
            }
        )
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )
        cls.auth_1.action_confirm()
        cls.http_client_profile_1 = cls.HttpClientProfile.create(
            {
                'name': 'MY-PROFILE-1',
                'base_url': DUMMY_URL,
                'auth_id': cls.auth_1.id,
            }
        )

    @responses.activate
    def test_01_apilog_outgoing_http_client_request_ok(self):
        # GIVEN
        url = DUMMY_URL + '/my_uri'
        responses.add(
            responses.POST,
            url,
            status=200,
            json={'receive': 10},
            headers={'Content-Type': 'application/json', 'MY-RESPONSE-HEADER-1': 'RH1'},
        )
        inp = RequestInput(
            method='POST',
            url=url,
            profile=self.http_client_profile_1,
            headers={'MY-REQUEST-HEADER-1': '123'},
            data_format_type=FORMAT_JSON,
            data={'send': 20},
            options={
                'apilog_vals': {'res_model': 'res.partner', 'res_id': 1, 'smth': 1}
            },
        )
        # WHEN
        self.HttpClient.send(inp)
        # THEN
        log = self.ApilogLog.search([('config_id', '=', self.apilog_config_1.id)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.request_body, '{"send":20}')
        self.assertEqual(log.response_body, '{"receive": 10}')
        self.assertEqual(log.res_model, 'res.partner')
        self.assertEqual(log.res_id, 1)
        req_headers = json.loads(log.request_headers)
        res_headers = json.loads(log.response_headers)
        self.assertEqual(req_headers['Content-Type'], 'application/json')
        self.assertEqual(req_headers['MY-REQUEST-HEADER-1'], '123')
        self.assertEqual(res_headers['MY-RESPONSE-HEADER-1'], 'RH1')

    @responses.activate
    def test_02_apilog_outgoing_http_client_request_error(self):
        # GIVEN
        url = DUMMY_URL + '/my_uri'
        responses.add(
            responses.POST,
            url,
            status=400,
            json={'error': 10},
            headers={'Content-Type': 'application/json', 'MY-RESPONSE-HEADER-1': 'RH1'},
        )
        inp = RequestInput(
            method='POST',
            url=url,
            profile=self.http_client_profile_1,
            headers={'MY-REQUEST-HEADER': '123'},
            data_format_type=FORMAT_JSON,
            data={'send': 20},
            options={
                'apilog_vals': {'res_model': 'res.partner', 'res_id': 1, 'smth': 1}
            },
        )
        # WHEN
        with mute_logger('odoo.addons.http_client.model_services.http_client'):
            self.HttpClient.send(inp)
        # THEN
        log = self.ApilogLog.search([('config_id', '=', self.apilog_config_1.id)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 400)
        self.assertEqual(log.request_body, '{"send":20}')
        self.assertEqual(log.response_body, '{"error": 10}')
        self.assertEqual(log.res_model, 'res.partner')
        self.assertEqual(log.res_id, 1)
        self.assertEqual(
            json.loads(log.request_headers)['Content-Type'], 'application/json'
        )
        self.assertEqual(
            json.loads(log.response_headers)['MY-RESPONSE-HEADER-1'], 'RH1'
        )
