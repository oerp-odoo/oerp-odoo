from . import common


class TestPackageConfiguratorBox(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.package_configurator_box_1 = cls.PackageConfiguratorBox.create(
            {
                'box_type_id': cls.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_id': cls.package_carton_1.id,
                'base_length': 0,
                'base_width': 0,
                'base_height': 0,
                'lid_height': 0,
                # price_unit == 2.0
                'lamination_outside_id': cls.package_lamination_1.id,
                'lamination_inside_id': cls.package_lamination_1.id,
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
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # THEN
        # Layouts
        self.assertEqual(cfg.base_layout_length, 194)
        self.assertEqual(cfg.base_layout_width, 71)
        self.assertEqual(cfg.base_inside_wrapping_length, 194)
        self.assertEqual(cfg.base_inside_wrapping_width, 71)
        self.assertEqual(cfg.base_outside_wrapping_length, 234)
        self.assertEqual(cfg.base_outside_wrapping_width, 111)
        self.assertEqual(cfg.lid_layout_length, 202)
        self.assertEqual(cfg.lid_layout_width, 79)
        # Wrapping
        self.assertEqual(cfg.lid_inside_wrapping_length, 202)
        self.assertEqual(cfg.lid_inside_wrapping_width, 79)
        self.assertEqual(cfg.lid_outside_wrapping_length, 242)
        self.assertEqual(cfg.lid_outside_wrapping_width, 119)
        # Lamination
        # (194*71+202*79) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_inside_area, 0.0356784)
        # 2 * 0.0356784
        self.assertEqual(cfg.lamination_inside_price, 0.0713568)
        # (234*111+242*119) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_outside_area, 0.06572639999999999)
        # 2 * 0.06572639999999999
        self.assertEqual(cfg.lamination_outside_price, 0.13145279999999998)

    def test_02_configure_box_missing_base_height(self):
        # WHEN
        cfg = self.package_configurator_box_1
        cfg.write(
            {
                'base_length': 165,
                'base_width': 42,
                'base_height': 0,
                'lid_height': 16,
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
        self.assertEqual(cfg.lamination_inside_area, 0)
        self.assertEqual(cfg.lamination_inside_price, 0)
        self.assertEqual(cfg.lamination_outside_area, 0)
        self.assertEqual(cfg.lamination_outside_price, 0)
