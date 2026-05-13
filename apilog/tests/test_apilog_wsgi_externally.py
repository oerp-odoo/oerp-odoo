from contextlib import contextmanager
from unittest.mock import patch

from odoo.tools import mute_logger

from .. import value_objects as vo
from ..patches import http as patched_http
from . import common


class TestApilogWsgiExternally(common.TestApilogCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.apilog_config_1 = cls.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
            }
        )

    def mock_get_env(self):
        @contextmanager
        def _get_env(db):
            yield self.env

        return _get_env

    def test_01_log_wsgi_ok(self):
        # GIVEN
        path = '/web/binary/company_logo'
        # WHEN
        # Patching to use the same env as is in tests, to make sure
        # data will be consistent during tests!
        with patch.object(
            patched_http, 'get_env', new=self.mock_get_env()
        ), patch.object(
            type(self.ApilogLog),
            'create',
        ) as mock_create:
            response = self.url_open(url=path)
        # THEN
        self.assertEqual(response.status_code, 200)
        mock_create.assert_called_once()
        vals = mock_create.call_args[0][0]
        self.assertTrue(vals.pop('request_headers'))
        self.assertTrue(vals.pop('response_headers'))
        self.assertEqual(
            vals,
            {
                'direction': 'incoming',
                'source': 'wsgi',
                'endpoint': 'http://127.0.0.1:8069/web/binary/company_logo',
                'http_verb': 'GET',
                'status_code': 200,
                'request_body': False,
                'response_traceback': False,
                'config_id': self.apilog_config_1.id,
            },
        )

    def test_02_log_wsgi_endpoint_not_found(self):
        # GIVEN
        path = '/not/existing/endpoint/123'
        # WHEN
        with patch.object(
            patched_http, 'get_env', new=self.mock_get_env()
        ), patch.object(type(self.ApilogHandler), '_create_log') as m:
            response = self.url_open(url=path)
            # THEN
            # For some reason in tests, when we get non 200 status code,
            # created logs don't persist and are not found. So for now
            # checking if actual create happened only.
            m.assert_called_once()
        self.assertEqual(response.status_code, 404)

    def test_03_log_wsgi_endpoint_redirect(self):
        # GIVEN
        path = '/report/download'
        # WHEN
        with patch.object(
            patched_http, 'get_env', new=self.mock_get_env()
        ), patch.object(type(self.ApilogHandler), '_create_log') as m:
            response = self.url_open(url=path, data='abc')
            # THEN
            # We have logs, one for calling /report/download, another
            # for redirecting to login (as this endpoint required to
            # login)
            self.assertEqual(m.call_count, 2)
        # This is response after redirection!
        self.assertEqual(response.status_code, 200)

    @mute_logger('odoo.http')
    def test_04_log_wsgi_endpoint_bad_data(self):
        # GIVEN
        path = '/web/login'
        # WHEN
        with patch.object(
            patched_http, 'get_env', new=self.mock_get_env()
        ), patch.object(type(self.ApilogHandler), '_create_log') as m:
            response = self.url_open(url=path, data='bad-data')
            # THEN
            self.assertEqual(m.call_count, 1)
        self.assertEqual(response.status_code, 400)

    def test_05_log_wsgi_no_active_apilog_config(self):
        # GIVEN
        self.apilog_config_1.active = False
        path = '/web/binary/company_logo'
        # WHEN
        with patch.object(
            patched_http, 'get_env', new=self.mock_get_env()
        ), patch.object(type(self.ApilogConfig), 'get_apilog_metadata') as m:
            response = self.url_open(url=path)
            # THEN
            self.assertEqual(m.call_count, 0)
        # THEN
        self.assertEqual(response.status_code, 200)
