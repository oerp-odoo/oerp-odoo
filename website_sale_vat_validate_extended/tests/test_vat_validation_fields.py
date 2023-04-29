from odoo.tests.common import TransactionCase

from ..controllers.website_sale import WebsiteSaleExtended


class TestVatValidationFields(TransactionCase):
    """Class to test extended validation fields."""

    def test_01_get_vat_validation_fields(self):
        """Check if new fields are included."""
        data = {
            'vat': 'LT1231231231',
            'name': 'Partner 1',
            'is_company': True,
        }
        res = WebsiteSaleExtended()._get_vat_validation_fields(data)
        self.assertEqual(res, dict(data, country_id=False))
