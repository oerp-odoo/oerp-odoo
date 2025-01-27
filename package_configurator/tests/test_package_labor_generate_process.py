from ..value_objects import labor as vo_labor
from . import common


class TestPackageLaborGenerateProcess(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PackageLaborProcessGeneration = cls.env['package.labor.process.generation']
        cls.labor_1 = cls.PackageLabor.create(
            {'name': 'MY-LABOR-1', 'sequence': 5, 'hour_cost': 25}
        )
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-KIND-1', 'package_type_id': cls.package_type_box.id}
        )
        cls.cfg_box = cls.PackageConfigurator.create(
            {
                'package_kind_id': cls.package_kind_box_1.id,
                'package_type_id': cls.package_type_box.id,
            },
        )
        cls.lamination_1 = cls.PackageLamination.create(
            {
                'name': 'Lamination 1',
                'unit_cost': 2,
            }
        )
        cls.area_1 = cls.PackageArea.create(
            {'pa_length': 10, 'pa_width': 10, 'uom_id': cls.uom_cm.id}
        )
        cls.foil_1 = cls.PackageFoil.create(
            {
                'area_range_from_id': cls.area_1.id,
                'form_cost': 50,
                'unit_cost': 0.1,
            }
        )

    def test_01_generate_no_labor_processes(self):
        # GIVEN
        self.PackageLaborItem.create(
            [
                {
                    'custom_name': 'MY-GENERIC-PROCESS-1',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 1000,
                    'setup_minutes': 30,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
            ]
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(res, [])

    def test_02_generate_labor_process_generic_base_only(self):
        # GIVEN
        self.PackageLaborItem.create(
            [
                {
                    'custom_name': 'MY-GENERIC-PROCESS-1',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 1000,
                    'setup_minutes': 30,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
                {
                    'custom_name': 'MY-GENERIC-PROCESS-2',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 100,
                    'setup_minutes': 0,
                    'to_fit': False,
                    'labor_id': self.labor_1.id,
                },
                # To be ignored.
                {
                    'labor_type_id': self.labor_type_lamination.id,
                    'units_per_hour': 50,
                    'setup_minutes': 0,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
            ]
        )
        self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': self.cfg_box.id,
            },
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='MY-GENERIC-PROCESS-1',
                    labor_type=self.labor_type_generic.code,
                    units_per_hour=1000,
                    setup_minutes=30,
                    component_type='base',
                    to_fit=True,
                ),
                vo_labor.LaborProcess(
                    name='MY-GENERIC-PROCESS-2',
                    labor_type=self.labor_type_generic.code,
                    units_per_hour=100,
                    setup_minutes=0,
                    component_type='base',
                    to_fit=False,
                ),
            },
        )

    def test_03_generate_labor_process_generic_base_n_lid(self):
        # GIVEN
        self.PackageLaborItem.create(
            [
                {
                    'custom_name': 'MY-GENERIC-PROCESS-1',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 1000,
                    'setup_minutes': 30,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
                # To be ignored.
                {
                    'labor_type_id': self.labor_type_lamination.id,
                    'units_per_hour': 50,
                    'setup_minutes': 0,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
            ]
        )
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='MY-GENERIC-PROCESS-1',
                    labor_type=self.labor_type_generic.code,
                    units_per_hour=1000,
                    setup_minutes=30,
                    component_type='base',
                    to_fit=True,
                ),
                vo_labor.LaborProcess(
                    name='MY-GENERIC-PROCESS-1',
                    labor_type=self.labor_type_generic.code,
                    units_per_hour=1000,
                    setup_minutes=30,
                    component_type='lid',
                    to_fit=True,
                ),
            },
        )

    def test_04_generate_labor_process_generic_base_n_lid_keep_base_only(self):
        # GIVEN
        self.PackageLaborItem.create(
            [
                {
                    'custom_name': 'MY-GENERIC-PROCESS-1',
                    'labor_type_id': self.labor_type_generic.id,
                    'units_per_hour': 1000,
                    'setup_minutes': 30,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
                # To be ignored.
                {
                    'labor_type_id': self.labor_type_lamination.id,
                    'units_per_hour': 50,
                    'setup_minutes': 0,
                    'to_fit': True,
                    'labor_id': self.labor_1.id,
                },
            ]
        )
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(
            self.labor_1, self.cfg_box, component_types=('base',)
        )
        # THEN
        self.assertEqual(
            res,
            [
                vo_labor.LaborProcess(
                    name='MY-GENERIC-PROCESS-1',
                    labor_type=self.labor_type_generic.code,
                    units_per_hour=1000,
                    setup_minutes=30,
                    component_type='base',
                    to_fit=True,
                ),
            ],
        )

    def test_05_generate_labor_process_wrappingpaper_cladding(self):
        # GIVEN
        (
            comp_base,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_wrappingpaper_cladding.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='Wrapping Paper Cladding',
                    labor_type=self.labor_type_wrappingpaper_cladding.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_inside',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Wrapping Paper Cladding',
                    labor_type=self.labor_type_wrappingpaper_cladding.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_outside',
                    to_fit=False,
                ),
            },
        )

    def test_06_generate_labor_process_lamination_inside_outside(self):
        # GIVEN
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        self.PackageConfiguratorLamination.create(
            [
                {
                    'configurator_id': self.cfg_box.id,
                    'side': 'inside',
                    'lamination_id': self.lamination_1.id,
                },
                {
                    'configurator_id': self.cfg_box.id,
                    'side': 'outside',
                    'lamination_id': self.lamination_1.id,
                },
            ]
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_lamination.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='Lamination',
                    labor_type=self.labor_type_lamination.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_inside',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Lamination',
                    labor_type=self.labor_type_lamination.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_outside',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Lamination',
                    labor_type=self.labor_type_lamination.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='lid_wrappingpaper_outside',
                    to_fit=False,
                ),
            },
        )

    def test_07_generate_labor_process_lamination_inside_only(self):
        # GIVEN
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_lid_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        self.PackageConfiguratorLamination.create(
            [
                {
                    'configurator_id': self.cfg_box.id,
                    'side': 'inside',
                    'lamination_id': self.lamination_1.id,
                },
            ]
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_lamination.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            res,
            [
                vo_labor.LaborProcess(
                    name='Lamination',
                    labor_type=self.labor_type_lamination.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_inside',
                    to_fit=False,
                ),
            ],
        )

    def test_08_generate_labor_process_foiling(self):
        # GIVEN
        comp_base, comp_wrappingpaper_inside = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        self.PackageConfiguratorFoil.create(
            [
                {
                    'configurator_id': self.cfg_box.id,
                    'component_id': comp_base.id,
                    'foil_id': self.foil_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_box.id,
                    'component_id': comp_base.id,
                    'foil_id': self.foil_1.id,
                    'side': 'outside',
                },
                {
                    'configurator_id': self.cfg_box.id,
                    'component_id': comp_wrappingpaper_inside.id,
                    'foil_id': self.foil_1.id,
                    'side': 'outside',
                },
            ],
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_foiling.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='Foiling',
                    labor_type=self.labor_type_foiling.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Foiling',
                    labor_type=self.labor_type_foiling.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Foiling',
                    labor_type=self.labor_type_foiling.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base_wrappingpaper_inside',
                    to_fit=False,
                ),
            },
        )

    def test_09_generate_labor_process_insert_putting(self):
        # GIVEN
        package_kind_insert_general = self.PackageKind.create(
            {'name': 'MY-GENERAL-1', 'package_type_id': self.package_type_insert.id}
        )
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        cfg_insert_1, cfg_insert_2 = self.PackageConfigurator.create(
            [
                {
                    'package_kind_id': package_kind_insert_general.id,
                    'package_type_id': self.package_type_insert.id,
                    'configurator_box_id': self.cfg_box.id,
                },
                {
                    'package_kind_id': package_kind_insert_general.id,
                    'package_type_id': self.package_type_insert.id,
                    'configurator_box_id': self.cfg_box.id,
                },
            ],
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_insert_putting.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(
            set(res),
            {
                vo_labor.LaborProcess(
                    name='Insert Putting',
                    labor_type=self.labor_type_insert_putting.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
                vo_labor.LaborProcess(
                    name='Insert Putting',
                    labor_type=self.labor_type_insert_putting.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
            },
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, cfg_insert_1)
        # THEN
        self.assertEqual(res, [])
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, cfg_insert_2)
        # THEN
        self.assertEqual(res, [])

    def test_10_generate_labor_process_insert_formation(self):
        # GIVEN
        package_kind_insert_general = self.PackageKind.create(
            {'name': 'MY-GENERAL-1', 'package_type_id': self.package_type_insert.id}
        )
        self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': self.cfg_box.id,
                },
            ]
        )
        cfg_insert_1, cfg_insert_2 = self.PackageConfigurator.create(
            [
                {
                    'package_kind_id': package_kind_insert_general.id,
                    'package_type_id': self.package_type_insert.id,
                    'configurator_box_id': self.cfg_box.id,
                },
                {
                    'package_kind_id': package_kind_insert_general.id,
                    'package_type_id': self.package_type_insert.id,
                    'configurator_box_id': self.cfg_box.id,
                },
            ],
        )
        self.PackageLaborItem.create(
            {
                'labor_type_id': self.labor_type_insert_formation.id,
                'units_per_hour': 1,
                'setup_minutes': 1,
                'to_fit': False,
                'labor_id': self.labor_1.id,
            }
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, self.cfg_box)
        # THEN
        self.assertEqual(res, [])
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, cfg_insert_1)
        # THEN
        self.assertEqual(
            res,
            [
                # All inserts by default are assumed to need Insert Formation labor!
                vo_labor.LaborProcess(
                    name='Insert Formation',
                    labor_type=self.labor_type_insert_formation.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
            ],
        )
        # WHEN
        res = self.PackageLaborProcessGeneration.generate(self.labor_1, cfg_insert_2)
        # THEN
        self.assertEqual(
            res,
            [
                # All inserts by default are assumed to need Insert Formation labor!
                vo_labor.LaborProcess(
                    name='Insert Formation',
                    labor_type=self.labor_type_insert_formation.code,
                    units_per_hour=1,
                    setup_minutes=1,
                    component_type='base',
                    to_fit=False,
                ),
            ],
        )
