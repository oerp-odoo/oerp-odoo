from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import common

PATCH_PATH = 'odoo.addons.base_vat.models.res_partner.ResPartner._check_vies'


# To auto fill some required fields when Form is used.
@common.tagged('-at_install', 'post_install')
class TestViesAutofill(common.TransactionCase):
    """Test class for VIES autofill functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for VIES autofill."""
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.partner_1 = cls.ResPartner.create({'name': 'Partner 2', 'is_company': True})
        cls.country_lt = cls.env.ref('base.lt')
        cls.company_main = cls.env.ref('base.main_company')
        cls.company_main.write(
            {
                'vat_check_vies': True,
                'vies_autofill': True,
            }
        )

    @patch(
        PATCH_PATH,
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': 'Street 1',
        },
    )
    def test_01_onchange_vat(self, _check_vies):
        """Retrieve company data from VIES when VAT is valid.

        Case: name and address included.
        """
        with common.Form(self.ResPartner) as partner:
            partner.is_company = True  # to trigger VIES in constraint
            partner.name = 'P2'
            partner.vat = 'LT123456'
            # Onchange must not replace already entered data.
            self.assertEqual(partner.name, 'P2')
            self.assertEqual(partner.country_id, self.country_lt)
            self.assertEqual(partner.street, 'Street 1')

    @patch(
        PATCH_PATH,
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': '---',
        },
    )
    def test_02_onchange_vat(self, _check_vies):
        """Retrieve company data from VIES when VAT is valid.

        Case: no address included.
        """
        with common.Form(self.ResPartner) as partner:
            partner.is_company = True
            partner.vat = 'LT123456'
            self.assertEqual(partner.name, 'P1')
            self.assertEqual(partner.country_id, self.country_lt)
            self.assertFalse(partner.street)

    @patch(
        PATCH_PATH,
        return_value={
            'valid': False,
            'countryCode': 'LT',
            'name': '---',
            'address': '---',
        },
    )
    def test_03_onchange_vat(self, _check_vies):
        """Retrieve company data from VIES when VAT is invalid."""
        # ResPartner = self.ResPartner.with_context(no_vat_validation=True)
        with self.assertRaises(ValidationError):
            with common.Form(self.ResPartner) as partner:
                partner.is_company = True
                # Passing valid VAT, to, make sure patch forced
                # valid=False return_value is used.
                partner.vat = 'LT100010958410'
                partner.name = 'P1'
                self.assertEqual(partner.country_id, self.country_lt)
                self.assertFalse(partner.street)

    @patch(
        PATCH_PATH,
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': '---',
        },
    )
    def test_04_retrieve_vies_data(self, _check_vies):
        """Try to retrieve company data when VIES autofill is disabled.

        Case 1: vat_check_vies=False.
        Case 2: vies_autofill=False.
        """
        # Case 1.
        self.company_main.vat_check_vies = False
        self.assertEqual(self.ResPartner.retrieve_vies_data('vat123'), {})
        # Case 2.
        self.company_main.write({'vat_check_vies': True, 'vies_autofill': False})
        self.assertEqual(self.ResPartner.retrieve_vies_data('vat123'), {})
