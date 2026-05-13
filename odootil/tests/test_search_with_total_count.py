from .common import TestOdootilCommon


class TestSearchWithTotalCount(TestOdootilCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1, cls.partner_2, cls.partner_3 = cls.ResPartner.create(
            [
                {
                    'name': 'MY-PARTNER-1',
                },
                {
                    'name': 'MY-PARTNER-2',
                },
                {
                    'name': 'MY-PARTNER-3',
                },
            ]
        )
        cls.partners = cls.partner_1 | cls.partner_2 | cls.partner_3

    def test_01_search_with_total_count_no_offset_no_limit(self):
        # WHEN
        partners, total_count = self.ResPartner.search_with_total_count(
            [('id', 'in', self.partners.ids)], order='id'
        )
        # THEN
        self.assertEqual(partners, self.partners)
        self.assertEqual(total_count, 3)

    def test_02_search_with_total_count_no_offset_w_limit(self):
        # WHEN
        partners, total_count = self.ResPartner.search_with_total_count(
            [('id', 'in', self.partners.ids)], limit=1
        )
        # THEN
        self.assertEqual(partners, self.partner_1)
        self.assertEqual(total_count, 3)

    def test_03_search_with_total_count_w_offset_no_limit(self):
        # WHEN
        partners, total_count = self.ResPartner.search_with_total_count(
            [('id', 'in', self.partners.ids)], offset=1
        )
        # THEN
        self.assertEqual(partners, self.partner_2 | self.partner_3)
        self.assertEqual(total_count, 3)

    def test_04_search_with_total_count_w_offset_w_limit(self):
        # WHEN
        partners, total_count = self.ResPartner.search_with_total_count(
            [('id', 'in', self.partners.ids)], offset=1, limit=1
        )
        # THEN
        self.assertEqual(partners, self.partner_2)
        self.assertEqual(total_count, 3)
