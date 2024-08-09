from odoo.addons.http_client.tests import common

from ..models.test_models import GROUP_CONTROLLER_XMLID


class TestHttpClientDemoCommon(common.TestHttpClientCommon):
    """Common class HTTP client demo tests."""

    @classmethod
    def setUpClass(cls):
        """Set up data for demo tests."""
        super().setUpClass()
        cls.HttpClientTestController = cls.env['http.client.test.controller']
        cls.HttpClientTestAuth = cls.env['http.client.test.auth']
        # Groups.
        cls.group_controller = cls.env.ref(GROUP_CONTROLLER_XMLID)
        # Connections.
        # Will use default company, which is main one.
        cls.test_auth_1 = cls.create_auth({})
        cls.company_2 = cls.env['res.company'].create(
            {'name': 'Second Test Company 123'}
        )
        # Second company.
        cls.test_auth_2 = cls.create_auth(
            {
                'auth_method': 'basic',
                'identifier': 'dummy',
                'secret': 'pass',
                'company_id': cls.company_2.id,
            }
        )
        # No company.
        cls.test_auth_3 = cls.create_auth({'company_id': False})
        # Confirm all.
        (cls.test_auth_1 | cls.test_auth_2 | cls.test_auth_3).action_confirm()
        # Enable controller.
        cls.group_user.implied_ids = [(4, cls.group_controller.id)]

    @classmethod
    def get_auth_model(cls):
        return cls.HttpClientTestAuth
