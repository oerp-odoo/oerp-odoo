from odoo.exceptions import ValidationError

from . import common


class TestHttpClientProfileConstraints(common.TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )

    def test_01_check_connection_base_url_ok(self):
        try:
            self.HttpClientProfile.create(
                {
                    'name': 'MY-CONNECTION-1',
                    'base_url': 'http://example.com',
                    'auth_id': self.auth_1.id,
                }
            )
        except ValidationError as e:
            self.fail(f"Must allowed to create connection. Error: {e}")

    def test_02_check_connection_base_url_incorrect(self):
        with self.assertRaisesRegex(
            ValidationError, r"'example\.com' is not valid URL\."
        ):
            self.HttpClientProfile.create(
                {
                    'name': 'MY-CONNECTION-1',
                    'base_url': 'example.com',
                    'auth_id': self.auth_1.id,
                }
            )
