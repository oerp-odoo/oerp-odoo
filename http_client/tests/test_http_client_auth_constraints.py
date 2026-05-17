from odoo.exceptions import ValidationError

from . import common


class TestHttpClientAuthConstraints(common.TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )

    def test_01_token_expire_delta_higher_than_zero(self):
        with self.assertRaisesRegex(
            ValidationError, r"Token Expire Delta must be 0 or lower!"
        ):
            self.auth_1.token_expire_delta = 100

    def test_02_bad_base_url(self):
        with self.assertRaisesRegex(
            ValidationError, r"'example\.com' is not valid URL\."
        ):
            self.auth_1.base_url = 'example.com'
