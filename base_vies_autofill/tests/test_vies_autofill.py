from unittest.mock import patch

from odoo.tests import Form, common

from ..models import res_partner as rp


# To auto fill some required fields when Form is used.
@common.tagged('-at_install', 'post_install')
class TestViesAutofill(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.country_lt = cls.env.ref('base.lt')
        cls.company_main = cls.env.ref('base.main_company')
        cls.company_main.write(
            {
                'vat_check_vies': True,
                'vies_autofill': True,
            }
        )

    @patch.object(
        rp,
        'check_vies',
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': 'Street 1',
        },
    )
    def test_01_onchange_vat_valid_address_included(self, _check_vies):
        with patch.object(
            type(self.ResPartner), '_check_vies_iap', return_value='valid'
        ):
            with Form(self.ResPartner.with_context(no_vat_validation=True)) as partner:
                partner.company_type = 'company'  # to trigger VIES in constraint
                partner.name = 'P2'
                partner.vat = 'LT123456'
                # Onchange must not replace already entered data.
                self.assertEqual(partner.name, 'P2')
                self.assertEqual(partner.country_id, self.country_lt)
                self.assertEqual(partner.street, 'Street 1')

    @patch.object(
        rp,
        'check_vies',
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': '---',
        },
    )
    def test_02_onchange_vat_valid_address_not_included(self, _check_vies):
        with patch.object(
            type(self.ResPartner), '_check_vies_iap', return_value='valid'
        ):
            with Form(self.ResPartner.with_context(no_vat_validation=True)) as partner:
                partner.company_type = 'company'  # to trigger VIES in constraint
                partner.name = 'P2'
                partner.vat = 'LT123456'
                # Onchange must not replace already entered data.
                self.assertEqual(partner.name, 'P2')
                self.assertEqual(partner.country_id, self.country_lt)
                self.assertFalse(partner.street)

    @patch.object(
        rp,
        'check_vies',
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': '---',
            'address': '---',
        },
    )
    def test_03_onchange_vat_invalid(self, _check_vies):
        with patch.object(
            type(self.ResPartner), '_check_vies_iap', return_value='invalid'
        ):
            with Form(self.ResPartner.with_context(no_vat_validation=True)) as partner:
                partner.name = 'P2'
                partner.company_type = 'company'  # to trigger VIES in constraint
                partner.vat = 'LT123456'
                self.assertEqual(partner.name, 'P2')
                self.assertEqual(partner.country_id, self.country_lt)
                self.assertFalse(partner.street)

    @patch.object(
        rp,
        'check_vies',
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': '---',
        },
    )
    def test_04_retrieve_vies_data_vat_check_vies_disabled(self, _check_vies):
        self.company_main.vat_check_vies = False
        self.assertEqual(self.ResPartner.retrieve_vies_data('vat123'), {})

    @patch.object(
        rp,
        'check_vies',
        return_value={
            'valid': True,
            'countryCode': 'LT',
            'name': 'P1',
            'address': '---',
        },
    )
    def test_05_retrieve_vies_data_vies_autofill_disabled(self, _check_vies):
        self.company_main.write({'vat_check_vies': True, 'vies_autofill': False})
        self.assertEqual(self.ResPartner.retrieve_vies_data('vat123'), {})
