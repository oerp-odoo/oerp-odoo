from ..value_objects.layout import Layout2D
from . import common


class TestPackageLaborMatch(common.TestProductPackageConfiguratorCommon):
    def test_01_labor_match_by_layout(self):
        # GIVEN
        l1, l2, l3 = self.PackageLabor.create(
            [
                {'name': 'MY-LABOR-1', 'sequence': 5, 'max_layout_length': 100},
                {'name': 'MY-LABOR-2', 'sequence': 20, 'max_layout_length': 800},
                {'name': 'MY-LABOR-3', 'sequence': 10, 'max_layout_length': 1000},
            ]
        )
        # WHEN
        res = (l1 | l2 | l3).match_labor(100, Layout2D(length=900, width=500))
        # THEN
        self.assertEqual(res, l3)

    def test_02_labor_match_by_min_quantity(self):
        # GIVEN
        l1, l2, l3 = self.PackageLabor.create(
            [
                {'name': 'MY-LABOR-1', 'sequence': 5, 'min_qty': 100},
                {'name': 'MY-LABOR-2', 'sequence': 10, 'min_qty': 800},
                {'name': 'MY-LABOR-3', 'sequence': 15, 'min_qty': 1000},
            ]
        )
        # WHEN
        res = (l1 | l2 | l3).match_labor(200, Layout2D(length=900, width=500))
        # THEN
        self.assertEqual(res, l1)

    def test_03_labor_match_by_max_quantity(self):
        # GIVEN
        l1, l2, l3 = self.PackageLabor.create(
            [
                {'name': 'MY-LABOR-1', 'sequence': 5, 'max_qty': 100},
                {'name': 'MY-LABOR-2', 'sequence': 10, 'max_qty': 800},
                {'name': 'MY-LABOR-3', 'sequence': 15, 'max_qty': 1000},
            ]
        )
        # WHEN
        res = (l1 | l2 | l3).match_labor(200, Layout2D(length=900, width=500))
        # THEN
        self.assertEqual(res, l2)
