import base64

from odoo.fields import Command

from odoo.addons.odootil.tools.crypto import make_hash
from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import value_objects as vo
from ..utils import unzip_from_base64
from . import common


class TestApilogHandler(common.TestApilogCommon):
    def test_01_apilog_handler_log_no_labels(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, '{"b": 20}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertFalse(log.label_ids)

    def test_02_apilog_handler_log_w_traceback(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=500,
            body='{"error": "internal-server-error"}',
            _headers={'MY-RESPONSE-HEADER-1': 'RH1'},
            traceback='my-traceback-1',
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 500)
        self.assertEqual(log.response_body, '{"error": "internal-server-error"}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertEqual(log.response_traceback, 'my-traceback-1')

    def test_03_apilog_handler_log_with_default_labels(self):
        # GIVEN
        labels = self.ApilogLabel.create([{'name': 'L1'}, {'name': 'L2'}])
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'label_ids': [Command.set(labels.ids)],
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
        )
        response = vo.ApilogResponse(status_code=200)
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, False)
        self.assertEqual(log.request_headers, '{}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, False)
        self.assertEqual(log.response_headers, '{}')
        self.assertEqual(log.label_ids, labels)

    def test_04_apilog_handler_log_with_default_n_extra_labels(self):
        # GIVEN
        secret = base64.b64encode(b'abc').decode()
        auth = f'Basic {secret}'
        fingerprint = make_hash(auth)
        label_1, label_2 = self.ApilogLabel.create([{'name': 'L1'}, {'name': 'L2'}])
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'label_ids': [Command.set(label_1.ids)],
                'config_label_ids': [
                    Command.create(
                        {
                            'label_id': label_2.id,
                            'match_expression': (
                                "inp.status_code == 200 and "
                                + f"inp.auth_fingerprint == '{fingerprint}'"
                            ),
                        }
                    )
                ],
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            _headers={'Authorization': auth},
        )
        response = vo.ApilogResponse(status_code=200)
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, False)
        self.assertEqual(
            log.request_headers,
            # We hash auth value!
            f'{{"Authorization": "{fingerprint}"}}',
        )
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, False)
        self.assertEqual(log.response_headers, '{}')
        self.assertEqual(log.label_ids, label_1 | label_2)

    def test_05_apilog_handler_no_log(self):
        # GIVEN
        self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': "inp.status_code == 401",
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log, self.ApilogLog)

    def test_06_apilog_handler_match_by_call_stack_function(self):
        # GIVEN
        # Wrapping in a function to use for match_expression!
        def my_func():
            return self.ApilogHandler.handle(
                vo.RequestDirection.INCOMING,
                'wsgi',
                request=request,
                response=response,
            )

        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': (
                    "('test_apilog_handler', 'my_func') in inp.call_stack"
                ),
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = my_func()
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, '{"b": 20}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertFalse(log.label_ids)

    def test_07_apilog_handler_match_by_call_stack_method(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': ("('apilog.handler', 'handle') in inp.call_stack"),
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, '{"b": 20}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertFalse(log.label_ids)

    def test_08_apilog_handler_log_w_extra_vals_wo_res_vals(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
            extra_vals={},
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, '{"b": 20}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertFalse(log.label_ids)
        self.assertFalse(log.res_model)
        self.assertFalse(log.res_id)

    def test_09_apilog_handler_log_w_extra_vals_w_res_vals(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
            extra_vals={'res_model': 'res.partner', 'res_id': 1},
        )
        # THEN
        self.assertEqual(log.direction, vo.RequestDirection.INCOMING)
        self.assertEqual(log.source, 'wsgi')
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertEqual(log.endpoint, 'http://localhost/my/path')
        self.assertEqual(log.http_verb, HttpVerb.GET)
        self.assertEqual(log.request_body, '{"a": 10}')
        self.assertEqual(log.request_headers, '{"MY-HEADER-1": "H1"}')
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.response_body, '{"b": 20}')
        self.assertEqual(log.response_body_value, b'{"b": 20}')
        self.assertEqual(log.response_headers, '{"MY-RESPONSE-HEADER-1": "RH1"}')
        self.assertFalse(log.label_ids)
        self.assertTrue(log.res_model, 'res.partner')
        self.assertTrue(log.res_id, 1)

    def test_10_apilog_handler_log_w_response_body_attachment(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'response_body_as_file': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200, body='{"b": 20}', _headers={'MY-RESPONSE-HEADER-1': 'RH1'}
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertFalse(log.response_body)
        data = log.response_body_file
        with unzip_from_base64(data) as zf:
            extracted_content = zf.read('response_body.txt')
        self.assertEqual(extracted_content, b'{"b": 20}')
        self.assertEqual(log.response_body_filename, 'response_body.zip')
        attachment = self.IrAttachment.search(
            [
                # We must pass res_field in domain, otherwise Odoo will
                # exclude it from search as it has special search rules
                # for binary fields saved on attachments!
                ('res_field', '=', 'response_body_file'),
                ('res_model', '=', 'apilog.log'),
                ('res_id', '=', log.id),
            ]
        )
        self.assertEqual(len(attachment), 1)
        self.assertEqual(log.response_body_value, b'{"b": 20}')
        # WHEN
        log.unlink()
        # THEN
        self.assertFalse(attachment.exists())

    def test_11_apilog_handler_log_w_response_body_json_attachment(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'response_body_as_file': True,
            }
        )
        request = vo.ApilogRequest(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            body='{"a": 10}',
            _headers={'MY-HEADER-1': 'H1'},
        )
        response = vo.ApilogResponse(
            status_code=200,
            body='{"b": 20}',
            _headers={
                'MY-RESPONSE-HEADER-1': 'RH1',
                'Content-Type': 'application/json',
            },
        )
        # WHEN
        log = self.ApilogHandler.handle(
            vo.RequestDirection.INCOMING,
            'wsgi',
            request=request,
            response=response,
        )
        # THEN
        self.assertEqual(log.config_id, apilog_config_1)
        self.assertFalse(log.response_body)
        data = log.response_body_file
        with unzip_from_base64(data) as zf:
            extracted_content = zf.read('response_body.json')
        self.assertEqual(extracted_content, b'{"b": 20}')
        self.assertEqual(log.response_body_filename, 'response_body.zip')
