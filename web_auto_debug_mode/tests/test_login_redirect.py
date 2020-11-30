from unittest.mock import patch

from odoo.tests import common

from ..controllers import main

from odoo.addons.web.controllers import main as web_main


class _MockedSession:
    uid = True


class _MockedRequest:
    def __init__(self, env):
        self.env = env
        self.session = _MockedSession()


class TestLoginRedirect(common.SavepointCase):
    """Class to test login redirect with debug mode."""

    @classmethod
    def setUpClass(cls):
        """Set up data for login redirect tests."""
        super(TestLoginRedirect, cls).setUpClass()
        # Patching in setUpClass, so it could be reused for tests
        # methods (patching needs to be the same in all cases).
        cls.patchers = cls._get_patchers()
        [p.start() for p in cls.patchers]
        cls.user_root = cls.env.ref('base.user_root')
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.home = main.HomeExtended()

    @classmethod
    def _get_patchers(cls):
        return [
            patch.object(main, 'request', _MockedRequest(cls.env)),
            patch.object(web_main, 'request', _MockedRequest(cls.env))
        ]

    def test_01_login_redirect(self):
        """No redirect for root/demo user."""
        redirect = self.home._login_redirect(self.user_root.id)
        self.assertEqual(redirect, '/web')
        redirect = self.home._login_redirect(self.user_demo.id)
        self.assertEqual(redirect, '/web')

    def test_02_login_redirect(self):
        """Debug redirect for admin user."""
        redirect = self.home._login_redirect(self.user_admin.id)
        self.assertEqual(redirect, '/web?debug=1')
        self.user_admin.debug_mode = 'debug_assets'
        redirect = self.home._login_redirect(self.user_admin.id)
        self.assertEqual(redirect, '/web?debug=assets')

    def test_03_login_redirect(self):
        """Debug redirect for admin user (website module installed)."""
        with patch.object(
                # For some reason website returns binary string instead
                # of normal string. And also append '?'.
                web_main.Home, '_login_redirect', return_value=b'/web?'):
            redirect = self.home._login_redirect(self.user_admin.id)
            self.assertEqual(redirect, '/web?debug=1')

    def test_04_login_redirect(self):
        """Ignore debug mode when exception redirect is used."""
        redirect = self.home._login_redirect(
            self.user_admin.id, redirect='/web/become')
        self.assertEqual(redirect, '/web/become')

    def test_05_login_redirect(self):
        """Not second debug mode, when one is already used."""
        redirect = self.home._login_redirect(
            self.user_admin.id, redirect='/web?debug')
        self.assertEqual(redirect, '/web?debug')
        redirect = self.home._login_redirect(
            self.user_admin.id, redirect='/web?debug=assets')
        self.assertEqual(redirect, '/web?debug=assets')

    def test_06_login_redirect(self):
        """Include debug mode when URL parameters are used."""
        redirect = self.home._login_redirect(
            self.user_admin.id,
            redirect='/web#action=32&model='
            'ir.module.module&view_type=list&menu_id=5')
        self.assertEqual(
            redirect,
            '/web?debug=1#action=32&model='
            'ir.module.module&view_type=list&menu_id=5')

    @classmethod
    def tearDownClass(cls):
        """Tear down patcher."""
        super(TestLoginRedirect, cls).tearDownClass()
        [p.stop() for p in cls.patchers]
