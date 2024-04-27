from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from odoo.addons.website_sale.controllers import main

from ..controllers import website_sale


class TestWebsiteGlobalPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_1 = cls.env.ref('website.default_website')
        cls.company_main = cls.env.ref('base.main_company')
        cls.sale_1 = cls.env.ref('sale.portal_sale_order_2')

    @patch.object(main, "request", MagicMock())
    @patch.object(website_sale, "request", MagicMock())
    def test_01_partner_values_postprocess_is_global_partner(self):
        # GIVEN
        main.request.website = self.website_1
        website_sale.request.website = self.website_1
        self.website_1.is_global_partner = True
        # WHEN
        res = website_sale.WebsiteSale().values_postprocess(
            self.sale_1, ('new', 'billing'), {}, [], ""
        )
        # THEN
        new_values = res[0]
        self.assertEqual(new_values['company_id'], False)

    @patch.object(main, "request", MagicMock())
    @patch.object(website_sale, "request", MagicMock())
    def test_02_partner_values_postprocess_is_not_global_partner(self):
        # GIVEN
        main.request.website = self.website_1
        website_sale.request.website = self.website_1
        self.website_1.is_global_partner = False
        # WHEN
        res = website_sale.WebsiteSale().values_postprocess(
            self.sale_1, ('new', 'billing'), {}, [], ""
        )
        # THEN
        new_values = res[0]
        self.assertEqual(new_values['company_id'], self.company_main.id)
