from odoo.tests.common import TransactionCase


class TestInterpolateCommonNote(TransactionCase):
    """Test class for interpolate_common_note functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up data."""
        super().setUpClass()
        cls.company_main = cls.env.ref('base.main_company')

    def test_01_interpolate_common_note(self):
        """Interpolate note, when it is False."""
        self.assertEqual(self.company_main.interpolate_common_note(), '')
        self.company_main.common_note = 'ABC123'

    def test_02_interpolate_common_note(self):
        """Interpolate note with plain text."""
        self.company_main.common_note = 'ABC123'
        # `p`, because field uses `html` widget.
        self.assertEqual(
            self.company_main.interpolate_common_note(), '<p>ABC123</p>'
        )

    def test_03_interpolate_common_note(self):
        """Interpolate note with company data placeholders."""
        self.company_main.common_note = '{company.name}-ABC'
        self.assertEqual(
            self.company_main.interpolate_common_note(),
            '<p>%s-ABC</p>' % self.company_main.name
        )
