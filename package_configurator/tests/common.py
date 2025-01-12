from odoo.tests.common import TransactionCase


class TestProductPackageConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.PackageArea = cls.env['package.area']
        cls.PackageStamp = cls.env['package.stamp']
        cls.PackageFoil = cls.env['package.foil']
        cls.PackagePrintHouse = cls.env['package.print.house']
        cls.PackageDefaultComponent = cls.env['package.default.component']
        cls.PackageSheetMatch = cls.env['package.sheet.match']
        cls.PackageConfigurator = cls.env['package.configurator']
        cls.PackageConfiguratorComponent = cls.env['package.configurator.component']
        cls.PackageConfiguratorStamp = cls.env['package.configurator.stamp']
        cls.PackageConfiguratorFoil = cls.env['package.configurator.foil']
        cls.PackageConfiguratorLamination = cls.env['package.configurator.lamination']
        cls.PackageConfiguratorCirculation = cls.env['package.configurator.circulation']
        cls.PackagePrintColor = cls.env['package.print.color']
        cls.PackageSetup = cls.env['package.setup']
        cls.PackageSetupRule = cls.env['package.setup.rule']
        cls.PackagePrintHouse = cls.env['package.print.house']
        cls.PackagePrintPricelist = cls.env['package.print.pricelist']
        cls.PackagePrintPricelistRule = cls.env['package.print.pricelist.rule']
        cls.PackageKind = cls.env['package.kind']
        cls.PackageSheetType = cls.env['package.sheet.type']
        cls.PackageSheet = cls.env['package.sheet']
        cls.PackageBoxLayout = cls.env['package.box.layout']
        cls.PackageLamination = cls.env['package.lamination']
        cls.uom_cm = cls.env.ref('uom.product_uom_cm')
        cls.package_type_box = cls.env.ref('package_configurator.package_type_box')
        cls.package_type_insert = cls.env.ref(
            'package_configurator.package_type_insert'
        )
        cls.component_kind_greyboard = cls.env.ref(
            'package_configurator.package_component_kind_greyboard'
        )
        cls.component_kind_carton = cls.env.ref(
            'package_configurator.package_component_kind_carton'
        )
        cls.component_kind_wrappingpaper = cls.env.ref(
            'package_configurator.package_component_kind_wrappingpaper'
        )
        cls.component_type_base = cls.env.ref(
            'package_configurator.package_component_type_base'
        )
        cls.component_type_lid = cls.env.ref(
            'package_configurator.package_component_type_lid'
        )
        cls.component_type_base_wrappingpaper_inside = cls.env.ref(
            'package_configurator.package_component_type_base_wrappingpaper_inside'
        )
        cls.component_type_base_wrappingpaper_outside = cls.env.ref(
            'package_configurator.package_component_type_base_wrappingpaper_outside'
        )
        cls.component_type_lid_wrappingpaper_inside = cls.env.ref(
            'package_configurator.package_component_type_lid_wrappingpaper_inside'
        )
        cls.component_type_lid_wrappingpaper_outside = cls.env.ref(
            'package_configurator.package_component_type_lid_wrappingpaper_outside'
        )
        # TODO: move these outside of common.
        (
            cls.package_sheet_type_greyboard_1,
            cls.package_sheet_type_wrappingpaper_1,
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
        cls.package_sheet_greyboard_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
                'component_kind_id': cls.component_kind_greyboard.id,
            }
        )
        cls.package_sheet_wrappingpaper_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 700,
                'sheet_width': 400,
                'unit_cost': 0.04,
                'component_kind_id': cls.component_kind_wrappingpaper.id,
            }
        )
        cls.package_sheet_wrappingpaper_2 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_wrappingpaper_1.id,
                'sheet_length': 800,
                'sheet_width': 400,
                'unit_cost': 0.06,
                'component_kind_id': cls.component_kind_wrappingpaper.id,
            }
        )
