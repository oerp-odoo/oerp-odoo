import datetime

from odoo.addons.odootil.tests.common import TestBaseCommon, update_create_date
from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import value_objects as vo
from . import common


class TestApilogRotator(common.TestApilogCommon, TestBaseCommon):
    def test_01_apilog_rotate_by_count(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'log_limit_count': 1,
            }
        )
        log_1, log_2 = self.ApilogLog.create(
            [
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
            ]
        )
        # WHEN
        res = self.ApilogRotator.rotate(
            vo.ApilogRotatorConfig.from_apilog_config(apilog_config_1)
        )
        # THEN
        self.assertEqual(res, 1)
        self.assertFalse(log_1.exists())
        self.assertTrue(log_2.exists())

    def test_02_apilog_rotate_by_days(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'log_limit_days': 10,
            }
        )
        log_1, log_2 = self.ApilogLog.create(
            [
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
            ]
        )
        # Make log_2 seem to be created long time ago.
        update_create_date(log_2, datetime.datetime(2022, 2, 19))
        # WHEN
        res = self.ApilogRotator.rotate(
            vo.ApilogRotatorConfig.from_apilog_config(apilog_config_1)
        )
        # THEN
        self.assertEqual(res, 1)
        self.assertTrue(log_1.exists())
        self.assertFalse(log_2.exists())

    def test_03_apilog_rotate_by_count_n_days(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'log_limit_days': 10,
                'log_limit_count': 2,
            }
        )
        log_1, log_2, log_3 = self.ApilogLog.create(
            [
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
            ]
        )
        update_create_date(log_2, datetime.datetime(2022, 2, 19))
        # WHEN
        res = self.ApilogRotator.rotate(
            vo.ApilogRotatorConfig.from_apilog_config(apilog_config_1)
        )
        # THEN
        self.assertEqual(res, 2)
        self.assertFalse(log_1.exists())
        self.assertFalse(log_2.exists())
        self.assertTrue(log_3.exists())

    def test_04_apilog_rotate_not_enabled(self):
        # GIVEN
        apilog_config_1 = self.ApilogConfig.create(
            {
                'name': 'MY-APILOG-CFG-1',
                'direction': vo.RequestDirection.INCOMING,
                'source': 'wsgi',
                'match_expression': 'True',
                'active': True,
                'log_limit_count': 0,
                'log_limit_days': 0,
            }
        )
        log_1, log_2 = self.ApilogLog.create(
            [
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
                {
                    'endpoint': 'http://localhost/abc',
                    'http_verb': HttpVerb.GET,
                    'status_code': 200,
                    'direction': vo.RequestDirection.INCOMING,
                    'source': 'wsgi',
                    'config_id': apilog_config_1.id,
                },
            ]
        )
        # WHEN
        res = self.ApilogRotator.rotate(
            vo.ApilogRotatorConfig.from_apilog_config(apilog_config_1)
        )
        # THEN
        self.assertEqual(res, 0)
        self.assertTrue(log_1.exists())
        self.assertTrue(log_2.exists())
