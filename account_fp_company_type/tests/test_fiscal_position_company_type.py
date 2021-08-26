from odoo.tests.common import SavepointCase


class TestFiscalPositionCompanyType(SavepointCase):
    """Test class for fiscal position detection by company type."""

    @classmethod
    def setUpClass(cls):
        """Set up data for FP company type tests."""
        super().setUpClass()
        cls.AccountFiscalPosition = cls.env['account.fiscal.position']
        cls.ResPartner = cls.env['res.partner']
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.partner_azure_freeman = cls.env.ref('base.res_partner_address_15')
        country_id = cls.partner_azure.country_id.id
        cls.partner_individual = cls.ResPartner.create({
            'name': 'Individual 1',
            'is_company': False,
            'country_id': country_id
        })
        cls.fp_no_company_type = cls.AccountFiscalPosition.create({
            'name': 'FP 1',
            'auto_apply': True,
            'country_id': country_id,
            'sequence': 5,
        })
        cls.fp_company = cls.AccountFiscalPosition.create({
            'name': 'FP 2',
            'auto_apply': True,
            'country_id': country_id,
            'company_type': 'company',
            'sequence': 10,
        })
        cls.fp_person = cls.AccountFiscalPosition.create({
            'name': 'FP 3',
            'auto_apply': True,
            'company_type': 'person',
            'country_id': country_id,
            'sequence': 15,
        })

    def test_01_get_fiscal_position(self):
        """Find fiscal position for company partner.

        Case 1: partner is company
        Case 2: partner is individual, but parent is company.
        """
        # Case 1.
        fp = self.AccountFiscalPosition.get_fiscal_position(
            self.partner_azure.id
        )
        self.assertEqual(fp, self.fp_company)
        # Case 2.
        fp = self.AccountFiscalPosition.get_fiscal_position(
            self.partner_azure_freeman.id
        )
        self.assertEqual(fp, self.fp_company)

    def test_02_get_fiscal_position(self):
        """Find fiscal position for individual partner.

        Case: only main partner passed.
        """
        fp = self.AccountFiscalPosition.get_fiscal_position(
            self.partner_individual.id
        )
        self.assertEqual(fp, self.fp_person)

    def test_03_get_fiscal_position(self):
        """Find fiscal position for individual partner.

        Case: also delivery_id is passed.
        """
        fp = self.AccountFiscalPosition.get_fiscal_position(
            self.partner_azure.id,
            delivery_id=self.partner_individual.id
        )
        self.assertEqual(fp, self.fp_person)

    def test_04_get_fiscal_position(self):
        """Find fiscal position when company_type can't be matched."""
        self.fp_company.country_id = self.env.ref('base.lt').id
        fp = self.AccountFiscalPosition.get_fiscal_position(
            self.partner_azure.id
        )
        self.assertEqual(fp, self.fp_no_company_type)
