from . import common


class TestPackageConfiguratorBox(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})

    def test_01_configure_box_basic(self):
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
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
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # # Lamination
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_inside_area, 0.0)
        # 2 * 0.0574944
        self.assertEqual(cfg.lamination_inside_unit_cost, 0.0)
        # (264*141+272*149) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_outside_area, 0.0)
        # 2 * 0.0933024
        self.assertEqual(cfg.lamination_outside_unit_cost, 0.0)
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 9)
        self.assertEqual(cfg.base_outside_fit_qty, 6)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 9)
        self.assertEqual(cfg.lid_outside_fit_qty, 5)

    def test_02_configure_box_w_lamination(self):
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                # unit_cost == 2.0
                'lamination_outside_id': self.package_lamination_1.id,
                'lamination_inside_id': self.package_lamination_1.id,
            }
        )
        # THEN
        # Lamination
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_inside_area, 0.0574944)
        # 2 * 0.0574944
        self.assertEqual(cfg.lamination_inside_unit_cost, 0.1149888)
        # (264*141+272*149) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_outside_area, 0.0933024)
        # 2 * 0.0933024
        self.assertEqual(cfg.lamination_outside_unit_cost, 0.1866048)

    def test_03_configure_box_with_circulation(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
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
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 9)
        self.assertEqual(cfg.base_outside_fit_qty, 6)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 9)
        self.assertEqual(cfg.lid_outside_fit_qty, 5)
        # Circulations
        # With 100 box circulation
        # 4 from base and 4 from lid
        self.assertEqual(circulation_1.total_base_carton_quantity, 4)
        self.assertEqual(circulation_1.total_lid_carton_quantity, 4)
        # 12 from base, 12 from lid
        self.assertEqual(circulation_1.total_base_inside_wrappingpaper_quantity, 12)
        self.assertEqual(circulation_1.total_lid_inside_wrappingpaper_quantity, 12)
        # 17 from base, 20 from lid.
        self.assertEqual(circulation_1.total_base_outside_wrappingpaper_quantity, 17)
        self.assertEqual(circulation_1.total_lid_outside_wrappingpaper_quantity, 20)
        self.assertEqual(circulation_1.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_1.total_lamination_outside_cost, 0.0)
        # 8*0.05 + 24*0.04 + 37*0.06
        self.assertEqual(circulation_1.total_cost, 3.5799999999999996)
        # 3.5799999999999996 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0358)
        # With 200 box circulation
        # 8 from base and 8 from lid
        self.assertEqual(circulation_2.total_base_carton_quantity, 8)
        self.assertEqual(circulation_2.total_lid_carton_quantity, 8)
        # 23 from base, 23 from lid
        self.assertEqual(circulation_2.total_base_inside_wrappingpaper_quantity, 23)
        self.assertEqual(circulation_2.total_lid_inside_wrappingpaper_quantity, 23)
        # 34 from base, 40 from lid.
        self.assertEqual(circulation_2.total_base_outside_wrappingpaper_quantity, 34)
        self.assertEqual(circulation_2.total_lid_outside_wrappingpaper_quantity, 40)
        self.assertEqual(circulation_2.total_lamination_inside_cost, 0.0)
        self.assertEqual(circulation_2.total_lamination_outside_cost, 0.0)
        # 16*0.05 + 46*0.04 + 74*0.06
        self.assertEqual(circulation_2.total_cost, 7.08)
        # 7.08 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0354)

    def test_04_configure_box_with_circulation_n_min_qty(self):
        # GIVEN
        self.package_carton_1.min_qty = 10
        # Inside
        self.package_wrappingpaper_1.min_qty = 24
        # Outside
        self.package_wrappingpaper_2.min_qty = 50
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
        )
        # THEN
        # Layouts
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 9)
        self.assertEqual(cfg.base_outside_fit_qty, 6)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 9)
        self.assertEqual(cfg.lid_outside_fit_qty, 5)
        # Circulations
        # With 100 box circulation
        # 4 from base and 4 from lid, but min_qty = 10
        self.assertEqual(circulation_1.total_base_carton_quantity, 5)
        self.assertEqual(circulation_1.total_lid_carton_quantity, 5)
        # 12 from base, 12 from lid and min_qty = 24
        self.assertEqual(circulation_1.total_base_inside_wrappingpaper_quantity, 12)
        self.assertEqual(circulation_1.total_lid_inside_wrappingpaper_quantity, 12)
        # 17 from base, 20 from lid. and min_qty = 50, so we increase it proportionally
        # 37/50 = 0.74 and then 17/0.74 = 23 (rounded up) and 20/0.74 = 27 (
        # rounded down)
        self.assertEqual(circulation_1.total_base_outside_wrappingpaper_quantity, 23)
        self.assertEqual(circulation_1.total_lid_outside_wrappingpaper_quantity, 27)
        # 10*0.05 + 24*0.04 + 50*0.06
        self.assertEqual(circulation_1.total_cost, 4.46)
        # 4.46 / 100
        self.assertEqual(circulation_1.unit_cost, 0.0446)
        # With 200 box circulation
        # 8 from base and 8 from lid
        self.assertEqual(circulation_2.total_base_carton_quantity, 8)
        self.assertEqual(circulation_2.total_lid_carton_quantity, 8)
        # 23 from base, 23 from lid
        self.assertEqual(circulation_2.total_base_inside_wrappingpaper_quantity, 23)
        self.assertEqual(circulation_2.total_lid_inside_wrappingpaper_quantity, 23)
        # 34 from base, 40 from lid.
        self.assertEqual(circulation_2.total_base_outside_wrappingpaper_quantity, 34)
        self.assertEqual(circulation_2.total_lid_outside_wrappingpaper_quantity, 40)
        # 16*0.05 + 46*0.04 + 74*0.06
        self.assertEqual(circulation_2.total_cost, 7.08)
        # 7.08 / 200
        self.assertEqual(circulation_2.unit_cost, 0.0354)

    def test_05_configure_box_with_circulation_n_lamination(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                # unit_cost == 2.0
                'lamination_outside_id': self.package_lamination_1.id,
                'lamination_inside_id': self.package_lamination_1.id,
            }
        )
        # WHEN
        circulation_1, circulation_2 = self.PackageConfiguratorBoxCirculation.create(
            [
                {'quantity': 100, 'configurator_id': cfg.id},
                {'quantity': 200, 'configurator_id': cfg.id},
            ]
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
        self.assertEqual(cfg.lid_inside_wrapping_length, 232)
        self.assertEqual(cfg.lid_inside_wrapping_width, 109)
        self.assertEqual(cfg.lid_outside_wrapping_length, 272)
        self.assertEqual(cfg.lid_outside_wrapping_width, 149)
        # Quantities
        # carton layout is 1000x700 (mm)
        # outside wrappingpaper layout is 800x400 (mm)
        # inside wrappingpaper layout is 700x400 (mm)
        self.assertEqual(cfg.base_layout_fit_qty, 27)
        self.assertEqual(cfg.base_inside_fit_qty, 9)
        self.assertEqual(cfg.base_outside_fit_qty, 6)
        self.assertEqual(cfg.lid_layout_fit_qty, 27)
        self.assertEqual(cfg.lid_inside_fit_qty, 9)
        self.assertEqual(cfg.lid_outside_fit_qty, 5)
        # Lamination
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_inside_area, 0.0574944)
        # 2 * 0.0574944
        self.assertEqual(cfg.lamination_inside_unit_cost, 0.1149888)
        # (264*141+272*149) * 1.2 / 1000000
        self.assertEqual(cfg.lamination_outside_area, 0.0933024)
        # 2 * 0.0933024
        self.assertEqual(cfg.lamination_outside_unit_cost, 0.1866048)
        # Circulations
        # With 100 box circulation
        # 4 from base and 4 from lid
        self.assertEqual(circulation_1.total_base_carton_quantity, 4)
        self.assertEqual(circulation_1.total_lid_carton_quantity, 4)
        # 12 from base, 12 from lid
        self.assertEqual(circulation_1.total_base_inside_wrappingpaper_quantity, 12)
        self.assertEqual(circulation_1.total_lid_inside_wrappingpaper_quantity, 12)
        # 17 from base, 20 from lid.
        self.assertEqual(circulation_1.total_base_outside_wrappingpaper_quantity, 17)
        self.assertEqual(circulation_1.total_lid_outside_wrappingpaper_quantity, 20)
        # Lamination cost
        # 0.1149888*100
        self.assertEqual(circulation_1.total_lamination_inside_cost, 11.49888)
        # 0.1866048*100
        self.assertEqual(circulation_1.total_lamination_outside_cost, 18.66048)
        # Last two is lamination.
        # 8*0.05 + 24*0.04 + 37*0.06 + 0.1149888*100 + 0.1866048*100
        self.assertEqual(circulation_1.total_cost, 33.73936)
        # 33.73936 / 100
        self.assertAlmostEqual(circulation_1.unit_cost, 0.337394, places=6)
        # With 200 box circulation
        # 8 from base and 8 from lid
        self.assertEqual(circulation_2.total_base_carton_quantity, 8)
        self.assertEqual(circulation_2.total_lid_carton_quantity, 8)
        # 23 from base, 23 from lid
        self.assertEqual(circulation_2.total_base_inside_wrappingpaper_quantity, 23)
        self.assertEqual(circulation_2.total_lid_inside_wrappingpaper_quantity, 23)
        # 34 from base, 40 from lid.
        self.assertEqual(circulation_2.total_base_outside_wrappingpaper_quantity, 34)
        self.assertEqual(circulation_2.total_lid_outside_wrappingpaper_quantity, 40)
        # 0.1149888*200
        self.assertEqual(circulation_2.total_lamination_inside_cost, 22.99776)
        # 0.1866048*200
        self.assertEqual(circulation_2.total_lamination_outside_cost, 37.32096)
        # Last two is lamination
        # 16*0.05 + 46*0.04 + 74*0.06 + 0.1149888*200 + 0.1866048*200
        self.assertEqual(circulation_2.total_cost, 67.39872)
        # 67.39872 / 200
        self.assertAlmostEqual(circulation_2.unit_cost, 0.336994, places=6)

    def test_06_configure_box_missing_base_height(self):
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'carton_base_id': self.package_carton_1.id,
                'carton_lid_id': self.package_carton_1.id,
                'wrappingpaper_base_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_base_outside_id': self.package_wrappingpaper_2.id,
                'wrappingpaper_lid_inside_id': self.package_wrappingpaper_1.id,
                'wrappingpaper_lid_outside_id': self.package_wrappingpaper_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 0.0,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                # unit_cost == 2.0
                'lamination_outside_id': self.package_lamination_1.id,
                'lamination_inside_id': self.package_lamination_1.id,
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
        self.assertEqual(cfg.lamination_inside_unit_cost, 0)
        self.assertEqual(cfg.lamination_outside_area, 0)
        self.assertEqual(cfg.lamination_outside_unit_cost, 0)
