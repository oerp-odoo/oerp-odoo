from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import value_objects as vo
from . import common


class TestApilogFormatter(common.TestApilogCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.apilog_config_1 = cls.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': "'/localhost/abc' in inp.endpoint",
                'active': True,
            }
        )

    def test_01_apilog_request_json_format(self):
        # WHEN
        log = self.ApilogLog.create(
            {
                'endpoint': 'http://localhost/abc',
                'http_verb': HttpVerb.GET,
                'status_code': 200,
                'request_body': '{"a": 10}',
                'request_headers': '{"Content-Type": "application/json"}',
                'response_body': '{"b": 10}',
                'response_headers': '{"Content-Type": "application/json"}',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'config_id': self.apilog_config_1.id,
            }
        )
        # THEN
        self.assertEqual(log.request_body_formatted, '{\n  "a": 10\n}')
        self.assertEqual(log.response_body_formatted, '{\n  "b": 10\n}')
        self.assertEqual(
            log.request_headers_formatted, '{\n  "Content-Type": "application/json"\n}'
        )
        self.assertEqual(
            log.response_headers_formatted, '{\n  "Content-Type": "application/json"\n}'
        )

    def test_02_apilog_request_body_json_no_json_header(self):
        # GIVEN, WHEN
        log = self.ApilogLog.create(
            {
                'endpoint': 'http://localhost/abc',
                'http_verb': HttpVerb.GET,
                'status_code': 200,
                'request_body': '{"a": 10}',
                'response_body': '{"b": 10}',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'config_id': self.apilog_config_1.id,
            }
        )
        # THEN
        self.assertEqual(log.request_body_formatted, '{"a": 10}')
        self.assertEqual(log.response_body_formatted, '{"b": 10}')
        self.assertEqual(log.request_headers_formatted, '{}')
        self.assertEqual(log.response_headers_formatted, '{}')

    def test_03_apilog_request_body_incorrect_json(self):
        # GIVEN, WHEN
        log = self.ApilogLog.create(
            {
                'endpoint': 'http://localhost/abc',
                'http_verb': HttpVerb.GET,
                'status_code': 200,
                'request_body': 'abc123',
                'response_body': 'abc456',
                'request_headers': '{"Content-Type": "application/json"}',
                'response_headers': '{"Content-Type": "application/json"}',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'config_id': self.apilog_config_1.id,
            }
        )
        # THEN
        self.assertEqual(log.request_body_formatted, 'abc123')
        self.assertEqual(log.response_body_formatted, 'abc456')
        self.assertEqual(
            log.request_headers_formatted, '{\n  "Content-Type": "application/json"\n}'
        )
        self.assertEqual(
            log.response_headers_formatted, '{\n  "Content-Type": "application/json"\n}'
        )
