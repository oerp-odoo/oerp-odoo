from odoo.exceptions import ValidationError

from . import common


class TestHttpClientConfigConstraints(common.TestHttpClientDemoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config_1 = cls.HttpClientConfig.create(
            {
                'model_controller_id': cls.http_client_test_controller_id,
            }
        )

    def test_01_http_client_config_wrong_controller_model(self):
        partner_model_id = self.IrModel._get('res.partner').id
        with self.assertRaisesRegex(ValidationError, r"Controller Model must inherit"):
            self.config_1.model_controller_id = partner_model_id
