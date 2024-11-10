from odoo.exceptions import ValidationError

from . import common


class TestPackageConfiguratorBoxConstraints(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.package_configurator_box_1 = cls.PackageConfiguratorBox.create(
            {
                'box_type_id': cls.package_box_type_1.id,
                'base_length': 10,
                'base_width': 10,
                'base_height': 10,
                'lid_height': 0,
            }
        )

    def test_01_check_cfg_box_length_less_than_min(self):
        self.package_box_type_1.min_length = 100
        # GIVEN
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Minimum box \(.+\) length is .+"
        ):
            self.package_configurator_box_1.base_length = 10

    def test_02_box_type_width_less_than_min(self):
        # GIVEN
        self.package_box_type_1.min_width = 100
        # WHEN
        res = self.package_box_type_1.validate_dimensions(10, 10, 10)
        # THEN
        self.assertEqual(res, {'length': True, 'width': False, 'height': True})

    def test_03_box_type_height_less_than_min(self):
        # GIVEN
        self.package_box_type_1.min_height = 100
        # WHEN
        res = self.package_box_type_1.validate_dimensions(10, 10, 10)
        # THEN
        self.assertEqual(res, {"length": True, "width": True, "height": False})

    def test_04_box_type_dimensions_ok(self):
        # GIVEN
        self.package_box_type_1.min_height = 10
        # WHEN
        res = self.package_box_type_1.validate_dimensions(10, 10, 10)
        # THEN
        self.assertEqual(res, {"length": True, "width": True, "height": True})
