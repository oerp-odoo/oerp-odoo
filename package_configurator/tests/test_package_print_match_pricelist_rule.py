from . import common


class TestPackagePrintMatchPricelistRule(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.color_1, cls.color_2 = cls.PackagePrintColor.create(
            [
                {'name': 'MY-COLOR-1'},
                {'name': 'MY-COLOR-2'},
            ]
        )
        cls.print_pricelist_1 = cls.PackagePrintPricelist.create(
            {'name': 'MY-PRICELIST-1'}
        )
        cls.print_house_1 = cls.PackagePrintHouse.create(
            {
                'name': 'MY-PRINTING-HOUSE-1',
                'print_pricelist_id': cls.print_pricelist_1.id,
            }
        )

    def test_01_match_pricelist_rule_various_options(self):
        # GIVEN
        rule_1, rule_2, rule_3 = self.PackagePrintPricelistRule.create(
            [
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 100,
                    'unit_cost': 3,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_1.id,
                    'min_qty': 200,
                    'unit_cost': 2,
                },
                {
                    'print_pricelist_id': self.print_pricelist_1.id,
                    'color_id': self.color_2.id,
                    'min_qty': 300,
                    'unit_cost': 1,
                },
            ]
        )
        # WHEN
        res = self.print_pricelist_1.match_rule(self.color_1, 500)
        # THEN
        self.assertEqual(res, rule_2)
        # WHEN
        res = self.print_pricelist_1.match_rule(self.color_1, 150)
        # THEN
        self.assertEqual(res, rule_1)
        # WHEN
        res = self.print_pricelist_1.match_rule(self.color_2, 50)
        # THEN
        self.assertEqual(res, self.PackagePrintPricelistRule)
        # WHEN
        res = self.print_pricelist_1.match_rule(self.color_2, 300)
        # THEN
        self.assertEqual(res, rule_3)
