from . import common


class TestPackageConfiguratorLaminationCost(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )
        cls.lamination_1 = cls.PackageLamination.create(
            {
                'name': 'Lamination 1',
                'unit_cost': 2,
            }
        )
        cls.sheet_greyboard_1, cls.sheet_wrappingpaper_1 = cls.PackageSheet.create(
            [
                {
                    'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                    'sheet_length': 1000,
                    'sheet_width': 700,
                    # On purpose to calc only foil cost!
                    'unit_cost': 0,
                    'component_kind_id': cls.component_kind_greyboard.id,
                },
                {
                    'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                    'sheet_length': 1000,
                    'sheet_width': 700,
                    # On purpose to calc only foil cost!
                    'unit_cost': 0,
                    'component_kind_id': cls.component_kind_wrappingpaper.id,
                },
            ]
        )
        cls.cfg_1 = cls.PackageConfigurator.create(
            {
                'package_kind_id': cls.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': cls.package_type_box.id,
            },
        )
        cls.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': cls.component_type_base.id,
                    'sheet_id': cls.sheet_greyboard_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
                {
                    'component_type_id': cls.component_type_lid.id,
                    'sheet_id': cls.sheet_greyboard_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': cls.sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': cls.sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
                {
                    'component_type_id': cls.component_type_lid_wrappingpaper_inside.id,
                    'sheet_id': cls.sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': cls.sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_1.id,
                },
            ]
        )

    def test_01_cfg_box_lamination_cost_single_lamination(self):
        # GIVEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        box_lamination = self.PackageConfiguratorLamination.create(
            {
                'configurator_id': self.cfg_1.id,
                'side': 'inside',
                'lamination_id': self.lamination_1.id,
            }
        )
        # THEN
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(box_lamination.area, 0.0574944)
        # 0.0574944 * 2
        self.assertEqual(box_lamination.area_unit_cost, 0.1149888)
        self.assertEqual(circ.total_lamination_cost, 11.49888)
        self.assertAlmostEqual(circ.unit_cost, 0.114989)
        self.assertEqual(circ.total_cost, 11.49888)

    def test_02_cfg_box_lamination_cost_two_lamination(self):
        # GIVEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        (
            box_lamination_1,
            box_lamination_2,
        ) = self.PackageConfiguratorLamination.create(
            [
                {
                    'configurator_id': self.cfg_1.id,
                    'lamination_id': self.lamination_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_1.id,
                    'lamination_id': self.lamination_1.id,
                    'side': 'outside',
                },
            ]
        )
        # THEN
        # (224*101+232*109) * 1.2 / 1000000
        self.assertEqual(box_lamination_1.area, 0.0574944)
        # 0.0574944 * 2
        self.assertEqual(box_lamination_1.area_unit_cost, 0.1149888)
        # (264*141+272*149) * 1.2 / 1000000
        self.assertEqual(box_lamination_2.area, 0.0933024)
        # 0.0933024 * 2
        self.assertEqual(box_lamination_2.area_unit_cost, 0.1866048)
        # 100 * 0.1149888 + 100 * 0.1866048
        self.assertEqual(circ.total_lamination_cost, 30.15936)
        self.assertAlmostEqual(circ.unit_cost, 0.301594)
        self.assertEqual(circ.total_cost, 30.15936)
