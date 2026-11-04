from odoo.tests.common import BaseCase

from ..value_objects.http import HttpVerb


class TestHttpVerb(BaseCase):
    def test_01_str_is_value(self):
        """Check verb stringifies to its value.

        Odoo 20.0 validates selection values by their string form, so
        a verb must be a valid selection value as is.
        """
        # GIVEN
        verb = HttpVerb.GET
        # THEN
        self.assertEqual(str(verb), 'GET')
        self.assertEqual(f'{verb}', 'GET')
        self.assertEqual(verb, 'GET')
