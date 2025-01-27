from . import common


def filter_processes(processes, component_type_code, name):
    return processes.filtered(
        lambda r: r.component_type_id.code == component_type_code and r.name == name
    )


class TestPackageConfiguratorLaborProcess(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )
        (
            package_sheet_type_greyboard_1,
            package_sheet_type_wrappingpaper_1,
        ) = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1.5,
                    'thickness_uom': 'mm',
                    'component_kind_id': cls.component_kind_greyboard.id,
                },
                {
                    'name': 'Some Art 1',
                    'thickness': 150,
                    'thickness_uom': 'gsm',
                    'component_kind_id': cls.component_kind_wrappingpaper.id,
                },
            ]
        )
        (
            package_sheet_greyboard_1,
            package_sheet_wrappingpaper_1,
            package_sheet_wrappingpaper_2,
        ) = cls.PackageSheet.create(
            [
                {
                    'sheet_type_id': package_sheet_type_greyboard_1.id,
                    'sheet_length': 1000,
                    'sheet_width': 700,
                    'unit_cost': 0.0,
                    'component_kind_id': cls.component_kind_greyboard.id,
                },
                {
                    'sheet_type_id': package_sheet_type_wrappingpaper_1.id,
                    'sheet_length': 700,
                    'sheet_width': 400,
                    'unit_cost': 0.0,
                    'component_kind_id': cls.component_kind_wrappingpaper.id,
                },
                {
                    'sheet_type_id': package_sheet_type_wrappingpaper_1.id,
                    'sheet_length': 800,
                    'sheet_width': 400,
                    'unit_cost': 0.0,
                    'component_kind_id': cls.component_kind_wrappingpaper.id,
                },
            ]
        )
        cls.cfg_box = cls.PackageConfigurator.create(
            {
                'package_kind_id': cls.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': cls.package_type_box.id,
            }
        )
        (
            cls.comp_base,
            cls.comp_lid,
            cls.comp_base_wrappingpaper_inside,
            cls.comp_base_wrappingpaper_outside,
            cls.comp_lid_wrappingpaper_inside,
            cls.comp_lid_wrappingpaper_outside,
        ) = cls.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': cls.component_type_base.id,
                    'sheet_id': package_sheet_greyboard_1.id,
                    'configurator_id': cls.cfg_box.id,
                },
                {
                    'component_type_id': cls.component_type_lid.id,
                    'sheet_id': package_sheet_greyboard_1.id,
                    'configurator_id': cls.cfg_box.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': package_sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_box.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': package_sheet_wrappingpaper_2.id,
                    'configurator_id': cls.cfg_box.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_lid_wrappingpaper_inside.id
                    ),
                    'sheet_id': package_sheet_wrappingpaper_1.id,
                    'configurator_id': cls.cfg_box.id,
                },
                {
                    'component_type_id': (
                        cls.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': package_sheet_wrappingpaper_2.id,
                    'configurator_id': cls.cfg_box.id,
                },
            ]
        )
        cls.area_1 = cls.PackageArea.create(
            {'pa_length': 10, 'pa_width': 10, 'uom_id': cls.uom_cm.id}
        )
        cls.foil_1 = cls.PackageFoil.create(
            {
                'area_range_from_id': cls.area_1.id,
                # To not affect total costs. We want to only check labor cost!
                'form_cost': 0,
                'unit_cost': 0.0,
            }
        )

    def test_01_configure_box_do_labor_init(self):
        # GIVEN
        labor_1 = self.PackageLabor.create(
            {
                'name': 'MY-LABOR-1',
                'sequence': 5,
                'hour_cost': 25,
                'default_hour_profit': 5,
            }
        )
        self.PackageLaborItem.create(
            [
                {
                    'custom_name': 'MY-GENERIC-PROCESS-1',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 1000,
                    'setup_minutes': 30,
                    'to_fit': False,
                    'labor_id': labor_1.id,
                },
                {
                    'labor_type_id': self.labor_type_foiling.id,
                    'units_per_hour': 100,
                    'setup_minutes': 15,
                    'to_fit': False,
                    'labor_id': labor_1.id,
                },
            ]
        )
        self.PackageConfiguratorFoil.create(
            [
                {
                    'configurator_id': self.cfg_box.id,
                    'component_id': self.comp_base.id,
                    'foil_id': self.foil_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_box.id,
                    'component_id': self.comp_base.id,
                    'foil_id': self.foil_1.id,
                    'side': 'outside',
                },
            ],
        )
        circulation_1 = self.PackageConfiguratorCirculation.create(
            [
                {'quantity': 500, 'configurator_id': self.cfg_box.id},
            ]
        )
        # WHEN
        self.cfg_box.action_labor_processes()
        # THEN
        circ_labor = circulation_1.circulation_labor_ids
        self.assertEqual(circ_labor.labor_id, labor_1)
        self.assertEqual(circ_labor.hour_profit, 5)
        self.assertEqual(len(circ_labor), 1)
        processes = circ_labor.process_ids
        # 2 generic (base+lid), 2 foiling (base)
        self.assertEqual(len(processes), 4)
        process_foiling_1, process_foiling_2 = filter_processes(
            processes, 'base', 'Foiling'
        )
        # Generic
        process_generic_base = filter_processes(
            processes, 'base', 'MY-GENERIC-PROCESS-1'
        )
        self.assertEqual(process_generic_base.labor_type_id, self.labor_type_generic)
        self.assertEqual(process_generic_base.units_per_hour, 1000)
        self.assertEqual(process_generic_base.setup_minutes, 30)
        # (500 / 1000) + 30 / 60
        self.assertEqual(process_generic_base.total_labor_hours, 1)
        # 1 * 25
        self.assertEqual(process_generic_base.total_cost, 25)
        # 25 / 500
        # We use digits to round the value and this actually causes imprecision (even
        # though it should simply be 0.05 value), because of binaries limitation to
        # represent floating points, so we ignore it.
        self.assertAlmostEqual(process_generic_base.unit_cost, 0.05, places=6)
        process_generic_lid = filter_processes(processes, 'lid', 'MY-GENERIC-PROCESS-1')
        self.assertEqual(process_generic_lid.labor_type_id, self.labor_type_generic)
        self.assertEqual(process_generic_lid.units_per_hour, 1000)
        self.assertEqual(process_generic_lid.setup_minutes, 30)
        # (500 / 1000) + 30 / 60
        self.assertEqual(process_generic_lid.total_labor_hours, 1)
        # 25 / 500
        self.assertAlmostEqual(process_generic_lid.unit_cost, 0.05, places=6)
        # 1 * 25
        self.assertEqual(process_generic_lid.total_cost, 25)
        # 25 / 500
        self.assertAlmostEqual(process_generic_lid.unit_cost, 0.05, places=6)
        # Foiling
        # Foiling base 1
        self.assertEqual(process_foiling_1.labor_type_id, self.labor_type_foiling)
        self.assertEqual(process_foiling_1.units_per_hour, 100)
        self.assertEqual(process_foiling_1.setup_minutes, 15)
        # (500 / 100) + 15 / 60
        self.assertEqual(process_foiling_1.total_labor_hours, 5.25)
        # 5.25 * 25
        self.assertEqual(process_foiling_1.total_cost, 131.25)
        # 131.25 / 500
        self.assertEqual(process_foiling_1.unit_cost, 0.2625)
        # Foiling base 2
        self.assertEqual(process_foiling_2.labor_type_id, self.labor_type_foiling)
        self.assertEqual(process_foiling_2.units_per_hour, 100)
        self.assertEqual(process_foiling_2.setup_minutes, 15)
        # (500 / 100) + 15 / 60
        self.assertEqual(process_foiling_2.total_labor_hours, 5.25)
        # (500 / 100) + 15 / 60
        # 5.25 * 25
        self.assertEqual(process_foiling_2.total_cost, 131.25)
        # 131.25 / 500
        self.assertEqual(process_foiling_2.unit_cost, 0.2625)
        # Totals
        # 1 + 1 + 5.25 + 5.25
        self.assertEqual(circ_labor.total_labor_hours, 12.5)
        # 25 + 25 + 131.25 + 131.25
        self.assertEqual(circ_labor.total_cost, 312.5)
        self.assertEqual(circ_labor.unit_cost, 0.625)
        self.assertEqual(circulation_1.total_cost, 312.5)
        self.assertEqual(circulation_1.unit_cost, 0.625)
        # Profit
        # 1*5 + 1*5 + 5.25*5 + 5.25*5
        self.assertEqual(circ_labor.total_profit, 62.5)
        # 62.5 / 500
        self.assertEqual(circ_labor.unit_profit, 0.125)
        # 62.5 + 312.5
        self.assertEqual(circ_labor.total_price, 375.0)
