from odoo.tests import common


class TestAuthBasicCommon(common.TransactionCase):
    """Common class for basic authentication tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for basic authentication tests."""
        super().setUpClass()
        cls.AuthBasic = cls.env['auth.basic']
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.auth_basic_1 = cls.AuthBasic.create(
            {
                'name': 'Project 1',
                'user_id': cls.user_admin.id,
                'username': 'demo',
                'password': 'demo_123',
            }
        )
