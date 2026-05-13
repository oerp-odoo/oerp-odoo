import json

import responses

from odoo.tools import mute_logger

from odoo.addons.apilog.tests.common import TestApilogCommon
from odoo.addons.apilog.value_objects import RequestDirection
from odoo.addons.http_client.tests.common import DUMMY_URL
from odoo.addons.http_client.value_objects import PathItem
from odoo.addons.http_client_demo.tests.common import TestHttpClientDemoCommon


class TestApilogHttpClient(TestApilogCommon, TestHttpClientDemoCommon):
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

    @responses.activate
    def test_01_apilog_outgoing_http_client_request_ok(self):
        # GIVEN
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(
            responses.POST,
            endpoint,
            status=200,
            json={'receive': 10},
            headers={'Content-Type': 'application/json', 'MY-RESPONSE-HEADER-1': 'RH1'},
        )
        # WHEN
        self.HttpClientTestController.call_http_method(
            'post',
            options={
                'path_item': PathItem(path_expression='my_uri'),
                'auth': self.test_auth_1,
                'kwargs': {'headers': {'my_header': '123'}, 'json': {'send': 20}},
                'extra_log_vals': {'res_model': 'res.partner', 'res_id': 1, 'smth': 1},
            },
        )
        # THEN
        log = self.ApilogLog.search([('config_id', '=', self.apilog_config_1.id)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.request_body, '{"send": 20}')
        self.assertEqual(log.response_body, '{"receive": 10}')
        self.assertEqual(log.res_model, 'res.partner')
        self.assertEqual(log.res_id, 1)
        self.assertEqual(
            json.loads(log.request_headers)['Content-Type'], 'application/json'
        )
        self.assertEqual(
            json.loads(log.response_headers)['MY-RESPONSE-HEADER-1'], 'RH1'
        )

    @responses.activate
    def test_02_apilog_outgoing_http_client_request_error(self):
        # GIVEN
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(
            responses.POST,
            endpoint,
            status=400,
            json={'error': 10},
            headers={'Content-Type': 'application/json', 'MY-RESPONSE-HEADER-1': 'RH1'},
        )
        # WHEN
        with mute_logger('odoo.addons.http_client.models.http_client_controller'):
            self.HttpClientTestController.call_http_method(
                'post',
                options={
                    'path_item': PathItem(path_expression='my_uri'),
                    'auth': self.test_auth_1,
                    'kwargs': {'headers': {'my_header': '123'}, 'json': {'send': 20}},
                    'extra_log_vals': {
                        'res_model': 'res.partner',
                        'res_id': 1,
                        'smth': 1,
                    },
                },
            )
        # THEN
        log = self.ApilogLog.search([('config_id', '=', self.apilog_config_1.id)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 400)
        self.assertEqual(log.request_body, '{"send": 20}')
        self.assertEqual(log.response_body, '{"error": 10}')
        self.assertEqual(log.res_model, 'res.partner')
        self.assertEqual(log.res_id, 1)
        self.assertEqual(
            json.loads(log.request_headers)['Content-Type'], 'application/json'
        )
        self.assertEqual(
            json.loads(log.response_headers)['MY-RESPONSE-HEADER-1'], 'RH1'
        )
