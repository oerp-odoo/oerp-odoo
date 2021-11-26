from odoo.tests.common import TransactionCase


class TestEori(TransactionCase):
    """Class to test EORI number field."""

    @classmethod
    def setUpClass(cls):
        """Set up data for eori tests."""
        super().setUpClass()
        cls.ResCompany = cls.env['res.company']
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.partner_azure_freeman = cls.env.ref('base.res_partner_address_15')

    def test_01_company_eori(self):
        """Create company to set EORI on related partner."""
        company = self.ResCompany.create(
            {'name': 'New Company 123', 'eori': 'E12345'}
        )
        self.assertEqual(company.partner_id.eori, company.eori)
        self.assertEqual(company.eori, 'E12345')

    def test_02_partner_eori(self):
        """Set EORI on commercial partner to sync with contacts."""
        self.partner_azure.eori = 'E54321'
        self.assertEqual(
            self.partner_azure_freeman.eori, self.partner_azure.eori
        )
        self.assertEqual(self.partner_azure_freeman.eori, 'E54321')
