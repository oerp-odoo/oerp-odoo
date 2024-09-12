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
        self.assertEqual(cfg.base_layout_length, 224)
        self.assertEqual(cfg.base_layout_width, 101)
        self.assertEqual(cfg.base_inside_wrapping_length, 224)
        self.assertEqual(cfg.base_inside_wrapping_width, 101)
        self.assertEqual(cfg.base_outside_wrapping_length, 264)
        self.assertEqual(cfg.base_outside_wrapping_width, 141)
        self.assertEqual(cfg.lid_layout_length, 232)
        self.assertEqual(cfg.lid_layout_width, 109)
        # Wrapping
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # Lamination
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_inside_area, 0.0574944)
        # 2 * 0.0574944
        self.assertEqual(cfg.lamination_inside_price, 0.1149888)
        # (264*141+272*149) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_outside_area, 0.0933024)
        # 2 * 0.0933024
        self.assertEqual(cfg.lamination_outside_price, 0.1866048)

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
