from odoo.tests.common import TransactionCase


class TestHandleName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HttpClientAuth = cls.env['http.client.auth']

    def test_01_handle_name_need_normalize(self):
        # GIVEN
        vals = {'name': 'My Auth_123!'}
        # WHEN
        self.HttpClientAuth.handle_name(vals)
        self.assertEqual(vals['name'], 'my_auth_123')

    def test_02_handle_name_not_need_normalize(self):
        # GIVEN
        vals = {'name': 'test_it'}
        # WHEN
        self.HttpClientAuth.handle_name(vals)
        self.assertEqual(vals['name'], 'test_it')

    def test_03_handle_name_no_name_in_vals(self):
        # GIVEN
        vals = {'xxx': 'abc'}
        # WHEN
        self.HttpClientAuth.handle_name(vals)
        self.assertEqual(vals, {'xxx': 'abc'})
