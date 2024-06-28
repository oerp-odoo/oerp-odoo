from odoo.addons.http_client.tests.common import (
    VALID_ACCESS_TOKEN_1,
    TestHttpClientCommon,
)


class TestApiSharepointCommon(TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SharepointAuth = cls.env['sharepoint.auth']
        cls.SharepointApi = cls.env['sharepoint.api']
        cls.SharepointSite = cls.env['sharepoint.site']
        cls.sharepoint_auth_1 = cls.create_auth(
            vals=dict(
                cls._get_dummy_bearer_client_credentials_auth_vals(),
                # To avoid calling login endpoint in tests.
                access_token=VALID_ACCESS_TOKEN_1,
            )
        )
        cls.sharepoint_auth_1.action_confirm()

    @classmethod
    def get_auth_model(cls):
        return cls.SharepointAuth
