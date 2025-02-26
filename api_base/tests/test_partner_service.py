from unittest.mock import patch

from odoo.exceptions import ValidationError

from ..pydantic_models import partner as pm_partner
from ..services.partner_service import PartnerService
from . import common


class TestPartnerService(common.TestApiBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_service = cls.base_services_env.component(usage='partners')

    def test_01_api_create_partner_ok(self):
        # GIVEN
        partner_in = pm_partner.PartnerInput(
            partner=pm_partner.Partner(
                name='My partner 1',
                partner_type='company',
                address_type='contact',
                street='street1',
                street2='street2',
                city='city1',
                country_code='lt',
                postal='p123',
                phone='123',
                mobile='234',
                email='a@b.com',
                website='abc.com',
            )
        )
        # WHEN
        with patch.object(
            PartnerService,
            '_prepare_partner_context',
            side_effect=PartnerService._prepare_partner_context,
            autospec=True,
        ) as m:
            response = self.partner_service.dispatch('create', params=partner_in.dict())
        # THEN
        partner = self.ResPartner.search([('id', '=', response['id'])])
        self.assertEqual(partner.name, 'My partner 1')
        self.assertEqual(partner.is_company, True)
        self.assertEqual(partner.type, 'contact')
        self.assertEqual(partner.street, 'street1')
        self.assertEqual(partner.city, 'city1')
        self.assertEqual(partner.country_id, self.country_lt)
        self.assertEqual(partner.zip, 'p123')
        self.assertEqual(partner.phone, '123')
        self.assertEqual(partner.mobile, '234')
        self.assertEqual(partner.website, 'http://abc.com')
        self.assertEqual(response['partner_type'], 'company')
        self.assertEqual(response['address_type'], 'contact')
        # Vat validation not ignored.
        self.assertEqual(m.side_effect(*m.call_args[0], **m.call_args[1]), {})

    def test_02_api_create_partner_no_vat_validation(self):
        # GIVEN
        partner_in = pm_partner.PartnerInput(
            partner=pm_partner.Partner(
                name='My partner 1',
                partner_type='company',
                address_type='contact',
                street='street1',
                street2='street2',
                city='city1',
                country_code='lt',
                postal='p123',
                phone='123',
                mobile='234',
                email='a@b.com',
                website='abc.com',
                # Note this won't necessary be validated, because this module
                # does not depend on base_vat. This is expected to only
                # pass necessary context and if VAT validation is used,
                # to ignore it.
                vat='LT123',
            ),
            vat_validation=False,
        )
        with patch.object(
            PartnerService,
            '_prepare_partner_context',
            side_effect=PartnerService._prepare_partner_context,
            autospec=True,
        ) as m:
            response = self.partner_service.dispatch('create', params=partner_in.dict())
        # THEN
        partner = self.ResPartner.search([('id', '=', response['id'])])
        self.assertEqual(partner.name, 'My partner 1')
        # Vat validation not ignored.
        # call_args first arg is positional args, second is keyword args!
        self.assertEqual(
            m.side_effect(*m.call_args[0], **m.call_args[1]),
            {'no_vat_validation': True},
        )

    def test_03_api_create_partner_contact_missing_name(self):
        # GIVEN
        partner_in = pm_partner.PartnerInput(
            partner=pm_partner.Partner(
                partner_type='company',
                address_type='contact',
                street='street1',
                street2='street2',
                city='city1',
                country_code='lt',
                postal='p123',
                phone='123',
                mobile='234',
                email='a@b.com',
                website='abc.com',
            )
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Name is required for Partner with AddressType as CONTACT"
        ):
            self.partner_service.dispatch('create', params=partner_in.dict())
