from odoo.exceptions import ValidationError

from .common import TestOdootilCommon


class TestConstraintHelpers(TestOdootilCommon):
    """Class to test various constraint helper methods."""

    def test_01_check_url(self):
        """Check valid url."""
        try:
            self.Odootil.check_url('http://www.myorg.eu')
            self.Odootil.check_url('https://www.myorg.eu')
            self.Odootil.check_url('ftp://www.myorg.eu')
            self.Odootil.with_context(skip_check_url=True).check_url(False)
        except ValidationError:
            self.fail("Valid URL must pass")

    def test_02_check_url(self):
        """Check invalid url."""
        with self.assertRaises(ValidationError):
            self.Odootil.check_url('httpxx://www.myorg')
        with self.assertRaises(ValidationError):
            self.Odootil.check_url('')
        with self.assertRaises(ValidationError):
            self.Odootil.check_url(False)
        with self.assertRaises(ValidationError):
            self.Odootil.check_url('www.myorg')
