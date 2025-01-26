from . import common


class TestPackageConfiguratorInsert(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_insert_general = cls.PackageKind.create(
            {'name': 'MY-GENERAL-1', 'package_type_id': cls.package_type_insert.id}
        )
        cls.package_sheet_type_carton_1 = cls.PackageSheetType.create(
            [
                {
                    'name': 'Orange/orange',
                    'thickness': 1,
                    'thickness_uom': 'mm',
                    'component_kind_id': cls.component_kind_carton.id,
                },
            ]
        )
        cls.package_sheet_carton_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_carton_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
                'component_kind_id': cls.component_kind_carton.id,
            }
        )

    def test_01_configure_insert_no_length_width(self):
        # WHEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_insert_general.id,
                'package_type_id': self.package_type_insert.id,
            },
        )
        (
            comp_base,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_carton_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # THEN
        # Layouts
        self.assertEqual(comp_base.component_length, 0)
        self.assertEqual(comp_base.component_width, 0)
        self.assertEqual(comp_base_wrappingpaper_inside.component_length, 0)
        self.assertEqual(comp_base_wrappingpaper_inside.component_width, 0)
        self.assertEqual(comp_base_wrappingpaper_outside.component_length, 0)
        self.assertEqual(comp_base_wrappingpaper_outside.component_width, 0)

    def test_02_configure_insert_custom_width_length(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_insert_general.id,
                'package_type_id': self.package_type_insert.id,
            },
        )
        (
            comp_base,
            comp_base_wrappingpaper_inside,
            comp_base_wrappingpaper_outside,
        ) = self.PackageConfiguratorComponent.create(
            [
                {
                    'component_type_id': self.component_type_base.id,
                    'sheet_id': self.package_sheet_carton_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_inside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_1.id,
                    'configurator_id': cfg.id,
                },
                {
                    'component_type_id': (
                        self.component_type_base_wrappingpaper_outside.id
                    ),
                    'sheet_id': self.package_sheet_wrappingpaper_2.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # WHEN
        comp_base.write({'_component_length': 100, '_component_width': 50})
        comp_base_wrappingpaper_inside.write(
            {'_component_length': 150, '_component_width': 80}
        )
        comp_base_wrappingpaper_outside.write(
            {'_component_length': 200, '_component_width': 90}
        )
        # THEN
        # Layouts
        # +30 comes from package_default_global_extra
        self.assertEqual(comp_base.component_length, 130)
        self.assertEqual(comp_base.component_width, 80)
        self.assertEqual(comp_base_wrappingpaper_inside.component_length, 180)
        self.assertEqual(comp_base_wrappingpaper_inside.component_width, 110)
        self.assertEqual(comp_base_wrappingpaper_outside.component_length, 230)
        self.assertEqual(comp_base_wrappingpaper_outside.component_width, 120)
