from odoo.fields import Command

from . import common


class TestPackageConfiguratorFoilCost(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
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
        cls.package_sheet_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                # On purpose to calc only foil cost!
                'unit_cost': 0,
                'component_kind_ids': [Command.set([cls.component_kind_greyboard.id])],
            }
        )
        cls.cfg_1 = cls.PackageConfigurator.create(
            {
                'box_type_id': cls.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': cls.package_type_box.id,
            },
        )
        cls.comp_base_greyboard = cls.PackageConfiguratorComponent.create(
            {
                'component_type_id': cls.component_type_base.id,
                'sheet_id': cls.package_sheet_1.id,
                'configurator_id': cls.cfg_1.id,
            },
        )

    def test_01_cfg_box_foil_cost_single_foil(self):
        # GIVEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        self.PackageConfiguratorFoil.create(
            {
                'configurator_id': self.cfg_1.id,
                'component_id': self.comp_base_greyboard.id,
                'foil_id': self.foil_1.id,
                'side': 'inside',
            }
        )
        # THEN
        # Only 1 item expected.
        circ_item = circ.item_ids[0]
        # 100 cut sheets are converted to raw sheets (so we get 4 raw sheets)
        # 50 + 0.1 * 4
        self.assertEqual(circ_item.foil_cost, 50.4)
        self.assertEqual(circ.unit_cost, 0.504)
        self.assertEqual(circ.total_cost, 50.4)

    def test_02_cfg_box_foil_cost_two_foils(self):
        # GIVEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        self.PackageConfiguratorFoil.create(
            [
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'foil_id': self.foil_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'foil_id': self.foil_1.id,
                    'side': 'outside',
                },
            ]
        )
        # THEN
        circ_item = circ.item_ids[0]
        # (50 + 0.1 * 4) + (50 + 0.1 * 4)
        self.assertEqual(circ_item.foil_cost, 100.8)
        self.assertEqual(circ.unit_cost, 1.008)
        self.assertEqual(circ.total_cost, 100.8)

    def test_03_cfg_box_foil_cost_with_setup(self):
        # GIVEN
        setup_1 = self.PackageBoxSetup.create(
            {
                'name': 'MY-BOX-FOIL-SETUP-1',
                'setup_type': 'foil',
            },
        )
        self.PackageBoxSetupRule.create(
            {'setup_id': setup_1.id, 'min_qty': 50, 'setup_fixed_qty': 20},
        )
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        self.PackageConfiguratorFoil.create(
            [
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'foil_id': self.foil_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'foil_id': self.foil_1.id,
                    'side': 'outside',
                },
            ]
        )
        # WHEN
        self.cfg_1.action_setup()
        # THEN
        circ_item = circ.item_ids[0]
        # Setup.
        self.assertEqual(len(circ_item.circulation_setup_ids), 1)
        circ_setup_foil = circ_item.circulation_setup_ids[0]
        self.assertEqual(circ_setup_foil.setup_id.setup_type, 'foil')
        # 20 cut sheets fit into single raw sheet
        self.assertEqual(circ_setup_foil.setup_raw_qty, 1)
        # Cost
        # (50 + 0.1 * (4+1)) + (50 + 0.1 * (4+1))
        self.assertEqual(circ_item.foil_cost, 101)
        self.assertEqual(circ.unit_cost, 1.01)
        self.assertEqual(circ.total_cost, 101)
