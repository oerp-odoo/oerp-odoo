from odoo.exceptions import ValidationError

from .. import utils
from . import common


class TestUtils(common.TestApiBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartnerTitle = cls.env['res.partner.title']
        cls.partner_1 = cls.ResPartner.create({'name': 'P111111'})
        cls.partner_title_1 = cls.ResPartnerTitle.create(
            {"name": "Ambassador", "shortcut": "Amb."}
        )

    def test_01_get_record_id_by_domain_match(self):
        # WHEN
        partner_id = utils.get_record_id_by_domain(
            self.ResPartner, domain=[('id', '=', self.partner_1.id)]
        )
        # THEN
        self.assertEqual(partner_id, self.partner_1.id)

    def test_02_get_record_id_by_domain_no_match(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"No Contact found using domain"):
            utils.get_record_id_by_domain(self.ResPartner, domain=[('id', '=', 0)])

    def test_03_get_record_id_by_name_match_multi(self):
        # GIVEN
        partner_2 = self.ResPartner.create({'name': 'P1231312'})
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Found more than one record"):
            utils.get_record_id_by_domain(
                self.ResPartner,
                domain=[('id', 'in', [self.partner_1.id, partner_2.id])],
            )

    def test_04_get_record_id_by_name_match(self):
        # WHEN
        partner_id = utils.get_record_id_by_name(
            self.ResPartner, name=self.partner_1.name
        )
        # THEN
        self.assertEqual(partner_id, self.partner_1.id)

    def test_05_get_record_id_by_name_match(self):
        # GIVEN
        name = 'MY-NEW-PARTNER-123'
        # WHEN
        partner_id = utils.get_record_id_by_name(
            self.ResPartner, name=name, force_create=True
        )
        # THEN
        partner = self.ResPartner.browse(partner_id)
        self.assertEqual(partner.name, name)

    def test_06_get_record_id_by_name_match_caseless(self):
        # GIVEN
        # WHEN
        partner_id = utils.get_record_id_by_name(
            self.ResPartner, name=self.partner_1.name.lower(), caseless=True
        )
        # THEN
        self.assertEqual(partner_id, self.partner_1.id)

    def test_07_validate_record_exists_n_active(self):
        self.assertEqual(utils.validate_record_exists(self.partner_1), '')

    def test_08_validate_record_exists(self):
        self.assertEqual(utils.validate_record_exists(self.partner_title_1), '')

    def test_09_validate_record_not_exists(self):
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Contact with ID .+ does not exist"
        ):
            utils.validate_record_exists(self.ResPartner)

    def test_10_validate_record_not_active(self):
        # GIVEN
        self.partner_1.active = False
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Contact with ID .+ does not exist"
        ):
            utils.validate_record_exists(self.partner_1)
