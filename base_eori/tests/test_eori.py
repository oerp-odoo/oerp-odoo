from odoo.tests.common import TransactionCase


class TestEori(TransactionCase):
    """Class to test EORI number field."""

    @classmethod
    def setUpClass(cls):
        """Set up data for eori tests."""
        super().setUpClass()
        cls.ResCompany = cls.env['res.company']
        cls.ResPartner = cls.env['res.partner']
        cls.partner_company = cls.ResPartner.create(
            {'name': 'MY-PARTNER-COMPANY-1', 'is_company': True}
        )
        cls.partner_contact = cls.ResPartner.create(
            {'name': 'MY-PARTNER-CONTACT-1', 'parent_id': cls.partner_company.id}
        )

    def test_01_company_eori(self):
        """Create company to set EORI on related partner."""
        company = self.ResCompany.create({'name': 'New Company 123', 'eori': 'E12345'})
        self.assertEqual(company.partner_id.eori, company.eori)
        self.assertEqual(company.eori, 'E12345')

    def test_02_partner_eori(self):
        """Set EORI on commercial partner to sync with contacts."""
        self.partner_company.eori = 'E54321'
        self.assertEqual(self.partner_contact.eori, self.partner_company.eori)
        self.assertEqual(self.partner_contact.eori, 'E54321')
