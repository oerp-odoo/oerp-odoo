from .common import TestOdootilCommon

PARTNER_TWIN_NAME = 'Twin Partner 111'


class TestSearchHelpers(TestOdootilCommon):
    """Test class for search helper methods."""

    @classmethod
    def setUpClass(cls):
        """Set up data for partner name_get search."""
        super().setUpClass()
        cls.ResPartnerCategory = cls.env['res.partner.category']
        cls.partner_1_name = cls.partner_1.name
        cls.partner_1_search_args = [('id', '=', cls.partner_1.id)]
        cls.company_2 = cls.ResCompany.create({'name': 'Company 2222222'})
        cls.partner_twin_1 = cls.ResPartner.create(
            {
                'name': PARTNER_TWIN_NAME,
                'company_id': cls.company_main.id,
            }
        )
        cls.partner_twin_2 = cls.ResPartner.create(
            {
                'name': PARTNER_TWIN_NAME,
                'company_id': cls.company_2.id,
            }
        )
        cls.partner_twins = cls.partner_twin_1 | cls.partner_twin_2

    def test_01_company_id_for_search(self):
        """Search when specific company is passed via context.

        Case 1: pass main company.
        Case 2: pass alternative company.
        Case 3: use explicit company in domain.
        Case 4: one company does have company_id set.
        """
        # Note. Can't use `name_search` here, because res.partner has
        # custom implementation it does not even call super in most
        # cases..
        # Case 1.
        partner = self.ResPartner.with_context(
            company_id_for_search=self.company_main.id
        ).search([('name', '=', PARTNER_TWIN_NAME)])
        self.assertEqual(partner, self.partner_twin_1)
        # Case 2.
        partner = self.ResPartner.with_context(
            company_id_for_search=self.company_2.id
        ).search([('name', '=', PARTNER_TWIN_NAME)])
        self.assertEqual(partner, self.partner_twin_2)
        # Case 3.
        partner = self.ResPartner.with_context(
            company_id_for_search=self.company_2.id
        ).search(
            [
                '&',
                ('name', '=', PARTNER_TWIN_NAME),
                ('company_id', '=', self.company_main.id),
            ]
        )
        self.assertEqual(partner, self.partner_twin_1)
        # Case 4.
        self.partner_twin_2.company_id = False
        partners = self.ResPartner.with_context(
            company_id_for_search=self.company_main.id
        ).search([('name', '=', PARTNER_TWIN_NAME)])
        self.assertCountEqual(partners, self.partner_twins)

    def test_02_company_id_for_search(self):
        """Try passing company context for model without company_id."""
        categ_1, categ_2 = self.ResPartnerCategory.create(
            [{'name': 'MY-CATEG-1'}, {'name': 'MY-CATEG-1'}]
        )
        categs = self.ResPartnerCategory.with_context(
            company_id_for_search=self.company_main.id
        ).search([('name', '=', 'MY-CATEG-1')])
        self.assertCountEqual(categs, categ_1 | categ_2)
