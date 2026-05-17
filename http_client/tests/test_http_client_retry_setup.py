from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..value_objects.session import HttpSessionSettingsRetry


class TestHttpClientRetrySetup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HttpClientRetry = cls.env['http.client.retry']

    def test_01_http_client_retry_all_disabled(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'retries_total': -1,
                'retries_connect': -1,
                'retries_read': -1,
                'retries_redirect': -1,
            }
        )
        # WHEN
        res = HttpSessionSettingsRetry.from_record(retry)
        # THEN
        self.assertEqual(res.retry.total, None)
        self.assertEqual(res.retry.connect, None)
        self.assertEqual(res.retry.read, None)
        self.assertEqual(res.retry.redirect, None)
        self.assertEqual(res.retry.backoff_factor, 0)
        # This is default that is put if nothing is specified.
        self.assertEqual(
            res.retry.allowed_methods,
            frozenset({'PUT', 'DELETE', 'OPTIONS', 'GET', 'HEAD', 'TRACE'}),
        )
        self.assertEqual(res.retry.status_forcelist, set())
        self.assertEqual(res.mount_prefixes, ('https://',))
        self.assertEqual(res.retry.raise_on_status, True)
        self.assertEqual(res.retry.raise_on_redirect, True)

    def test_02_http_client_retry_all_set(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'mount_prefixes': 'http://, https://',
                'retries_total': 5,
                'retries_connect': 1,
                'retries_read': 2,
                'retries_redirect': 3,
                'backoff_factor': 0.1,
                'allowed_methods': 'GET, POST',
                'status_forcelist': '500, 501, 502',
            }
        )
        # WHEN
        res = HttpSessionSettingsRetry.from_record(retry)
        # THEN
        self.assertEqual(res.retry.total, 5)
        self.assertEqual(res.retry.connect, 1)
        self.assertEqual(res.retry.read, 2)
        self.assertEqual(res.retry.redirect, 3)
        self.assertEqual(res.retry.backoff_factor, 0.1)
        # This is default that is put if nothing is specified.
        self.assertEqual(res.retry.allowed_methods, frozenset(['GET', 'POST']))
        self.assertEqual(res.retry.status_forcelist, frozenset([500, 501, 502]))
        self.assertEqual(
            res.mount_prefixes,
            (
                'http://',
                'https://',
            ),
        )

    def test_03_http_client_retry_raise_disabled(self):
        # GIVEN
        retry = self.HttpClientRetry.create(
            {
                'name': 'MY-RETRY-1',
                'raise_on_status': False,
                'raise_on_redirect': False,
            }
        )
        # WHEN
        res = HttpSessionSettingsRetry.from_record(retry)
        # THEN
        self.assertEqual(res.retry.raise_on_status, False)
        self.assertEqual(res.retry.raise_on_redirect, False)

    def test_04_http_client_retry_allowed_methods_lowercase(self):
        with self.assertRaisesRegex(
            ValidationError, r"Allowed Methods must be uppercased"
        ):
            self.HttpClientRetry.create(
                {
                    'name': 'MY-RETRY-1',
                    'allowed_methods': 'put',
                }
            )

    def test_05_http_client_retry_allowed_methods_wrong_method(self):
        with self.assertRaisesRegex(
            ValidationError, r"Incorrect allowed method \(.+\) used\. Valid methods: .+"
        ):
            self.HttpClientRetry.create(
                {
                    'name': 'MY-RETRY-1',
                    'allowed_methods': 'SOMETHING, POST',
                }
            )

    def test_06_http_client_retry_status_forcelist_not_integer(self):
        with self.assertRaisesRegex(
            ValidationError,
            r"Status Forcelist must be positive comma separated integers",
        ):
            self.HttpClientRetry.create(
                {
                    'name': 'MY-RETRY-1',
                    'status_forcelist': 'abc, 500',
                }
            )

    def test_07_http_client_retry_status_forcelist_negative_integer(self):
        with self.assertRaisesRegex(
            ValidationError,
            r"Status Forcelist must be positive comma separated integers",
        ):
            self.HttpClientRetry.create(
                {
                    'name': 'MY-RETRY-1',
                    'status_forcelist': '-500, 500',
                }
            )
