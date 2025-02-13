import datetime

import responses

from odoo.tools.misc import mute_logger

from odoo.addons.http_client import value_objects as vo
from odoo.addons.http_client.tests.common import DUMMY_URL, HTTP_CLIENT_MODULE_PATH

from . import common


class TestHttpClientLog(common.TestHttpClientDemoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HttpClientLogRotation = cls.env['http.client.log.rotation']
        cls.HttpClientLog = cls.env['http.client.log']
        cls.IrModel = cls.env['ir.model']
        cls.config_1 = cls.HttpClientConfig.create(
            {
                'model_controller_id': cls.http_client_test_controller_id,
                'log_enabled': True,
            }
        )

    @responses.activate
    def test_01_http_client_log_post(self):
        # GIVEN
        path_expr = '/my_uri'
        endpoint = DUMMY_URL + path_expr
        responses.add(responses.POST, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'post',
            options={
                'path_item': vo.PathItem(path_expression=path_expr),
                'auth': self.test_auth_1,
                'kwargs': {'headers': {'my_header': '123'}, 'json': {'send': 20}},
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.model_controller_id.model, 'http.client.test.controller')
        self.assertEqual(log.request_body, '{"send": 20}')
        self.assertEqual(log.response_body, '{"receive": 10}')

    @responses.activate
    def test_02_http_client_log_post_error(self):
        # GIVEN
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.POST, endpoint, status=401, json={'error': 10})
        # WHEN
        with mute_logger(HTTP_CLIENT_MODULE_PATH):
            self.HttpClientTestController.call_http_method(
                'post',
                options={
                    'endpoint': endpoint,
                    'auth': self.test_auth_1,
                    'kwargs': {'headers': {'my_header': '123'}, 'json': {'send': 20}},
                },
            )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'POST')
        self.assertEqual(log.status_code, 401)
        self.assertEqual(log.model_controller_id.model, 'http.client.test.controller')
        self.assertEqual(log.request_body, '{"send": 20}')
        self.assertEqual(log.response_body, '{"error": 10}')

    @responses.activate
    def test_03_http_client_log_get(self):
        # GIVEN
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'GET')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.model_controller_id.model, 'http.client.test.controller')
        self.assertEqual(log.request_body, False)
        self.assertEqual(log.response_body, '{"receive": 10}')

    @responses.activate
    def test_04_http_client_log_not_filtered_out(self):
        # GIVEN
        self.config_1.log_status_code_filter = '<250'
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 1)

    @responses.activate
    def test_05_http_client_log_filtered_out(self):
        # GIVEN
        self.config_1.log_status_code_filter = '>250'
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 0)

    @responses.activate
    def test_06_http_client_log_cfg_inactive(self):
        # GIVEN
        self.config_1.active = False
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 0)

    @responses.activate
    def test_07_http_client_log_logging_disabled(self):
        # GIVEN
        self.config_1.log_enabled = False
        endpoint = DUMMY_URL + '/my_uri'
        responses.add(responses.GET, endpoint, status=200, json={'receive': 10})
        # WHEN
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # THEN
        log = self.HttpClientLog.search([('endpoint', '=', endpoint)])
        self.assertEqual(len(log), 0)

    @responses.activate
    def test_08_http_client_log_rotate_by_limit(self):
        # GIVEN
        endpoint_1 = DUMMY_URL + '/my_uri'
        endpoint_2 = DUMMY_URL + '/my_uri2'
        responses.add(responses.GET, endpoint_1, status=200, json={'receive': 10})
        responses.add(responses.GET, endpoint_2, status=200, json={'receive': 10})
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint_1,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint_2,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # WHEN
        res = self.HttpClientLogRotation.rotate(
            vo.Config(
                controller_model=self.HttpClientTestController._name,
                log=vo.LogConfig(enabled=True, limit_count=1),
            )
        )
        # THEN
        self.assertEqual(res, 1)
        log_old = self.HttpClientLog.search([('endpoint', '=', endpoint_1)])
        self.assertFalse(log_old)
        log = self.HttpClientLog.search([('endpoint', '=', endpoint_2)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'GET')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.model_controller_id.model, 'http.client.test.controller')
        self.assertEqual(log.request_body, False)
        self.assertEqual(log.response_body, '{"receive": 10}')

    @responses.activate
    def test_09_http_client_log_rotate_by_days(self):
        # GIVEN
        self.config_1.log_limit_days = 10
        endpoint_1 = DUMMY_URL + '/my_uri'
        endpoint_2 = DUMMY_URL + '/my_uri2'
        responses.add(responses.GET, endpoint_1, status=200, json={'receive': 10})
        responses.add(responses.GET, endpoint_2, status=200, json={'receive': 10})
        # Outdated log
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint_1,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        log_old = self.HttpClientLog.search([('endpoint', '=', endpoint_1)])
        self._update_create_date(log_old, datetime.datetime(2022, 2, 19))
        # Recent log
        self.HttpClientTestController.call_http_method(
            'get',
            options={
                'endpoint': endpoint_2,
                'auth': self.test_auth_1,
                'kwargs': {
                    'headers': {'my_header': '123'},
                },
            },
        )
        # WHEN
        self.HttpClientLogRotation._gc_rotate()
        # THEN
        self.assertFalse(log_old.exists())
        log = self.HttpClientLog.search([('endpoint', '=', endpoint_2)])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.http_verb, 'GET')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.model_controller_id.model, 'http.client.test.controller')
        self.assertEqual(log.request_body, False)
        self.assertEqual(log.response_body, '{"receive": 10}')
