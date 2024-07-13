from . import common


class TestPackageConfiguratorBox(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.package_configurator_box_1 = cls.PackageConfiguratorBox.create(
            {
                'box_type_id': cls.package_box_type_1.id,
                'base_length': 0,
                'base_width': 0,
                'base_height': 0,
                'lid_height': 0,
            }
        )

    def test_01_configure_box(self):
        # WHEN
        cfg = self.package_configurator_box_1
        cfg.write(
            {
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_thickness': 1.5,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # THEN
        self.assertEqual(cfg.base_layout_length, 194)
        self.assertEqual(cfg.base_layout_width, 71)
        self.assertEqual(cfg.base_inside_wrapping_length, 194)
        self.assertEqual(cfg.base_inside_wrapping_width, 71)
        self.assertEqual(cfg.base_outside_wrapping_length, 214)
        self.assertEqual(cfg.base_outside_wrapping_width, 91)
        self.assertEqual(cfg.lid_layout_length, 202)
        self.assertEqual(cfg.lid_layout_width, 79)
        self.assertEqual(cfg.lid_inside_wrapping_length, 202)
        self.assertEqual(cfg.lid_inside_wrapping_width, 79)
        self.assertEqual(cfg.lid_outside_wrapping_length, 222)
        self.assertEqual(cfg.lid_outside_wrapping_width, 99)

    def test_02_configure_box_missing_base_height(self):
        # WHEN
        cfg = self.package_configurator_box_1
        cfg.write(
            {
                'base_length': 165,
                'base_width': 42,
                'base_height': 0,
                'lid_height': 16,
                'lid_thickness': 1.5,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # THEN
        self.assertEqual(cfg.base_layout_length, 0)
        self.assertEqual(cfg.base_layout_width, 0)
        self.assertEqual(cfg.base_inside_wrapping_length, 0)
        self.assertEqual(cfg.base_inside_wrapping_width, 0)
        self.assertEqual(cfg.base_outside_wrapping_length, 0)
        self.assertEqual(cfg.base_outside_wrapping_width, 0)
        self.assertEqual(cfg.lid_layout_length, 0)
        self.assertEqual(cfg.lid_layout_width, 0)
        self.assertEqual(cfg.lid_inside_wrapping_length, 0)
        self.assertEqual(cfg.lid_inside_wrapping_width, 0)
        self.assertEqual(cfg.lid_outside_wrapping_length, 0)
        self.assertEqual(cfg.lid_outside_wrapping_width, 0)
