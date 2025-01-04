from .. import const
from . import common


class TestPackageConfiguratorStampCost(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})
        cls.area_1 = cls.PackageArea.create(
            {'pa_length': 10, 'pa_width': 10, 'uom_id': cls.uom_cm.id}
        )
        cls.stamp_1 = cls.PackageStamp.create(
            {
                'area_range_from_id': cls.area_1.id,
                'stamp_type': 'emboss',
                'tool_cost': 50,
            }
        )
        cls.package_sheet_1 = cls.PackageSheet.create(
            {
                'sheet_type_id': cls.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                # On purpose to calc only stamp cost!
                'unit_cost': 0,
                'scope': const.SheetTypeScope.GREYBOARD,
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
            },
        )
        cls.comp_base_greyboard = cls.PackageConfiguratorComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': cls.package_sheet_1.id,
                'configurator_id': cls.cfg_1.id,
            },
        )

    def test_01_cfg_box_stamp_cost_single_stamp(self):
        # GIVEN
        self.PackageConfiguratorStamp.create(
            {
                'configurator_id': self.cfg_1.id,
                'component_id': self.comp_base_greyboard.id,
                'stamp_id': self.stamp_1.id,
                'side': 'inside',
            }
        )
        # WHEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # THEN
        # Only 1 item expected.
        circ_item = circ.item_ids[0]
        self.assertEqual(circ_item.stamp_cost, 50)
        self.assertEqual(circ.unit_cost, 0.5)
        self.assertEqual(circ.total_cost, 50)

    def test_02_cfg_box_stamp_cost_two_stamps(self):
        # GIVEN
        self.PackageConfiguratorStamp.create(
            [
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'stamp_id': self.stamp_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'stamp_id': self.stamp_1.id,
                    'side': 'outside',
                },
            ]
        )
        # WHEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # THEN
        circ_item = circ.item_ids[0]
        self.assertEqual(circ_item.stamp_cost, 100)
        self.assertEqual(circ.unit_cost, 1)
        self.assertEqual(circ.total_cost, 100)

    def test_03_cfg_box_stamp_cost_single_stamp_with_foil(self):
        # GIVEN
        self.stamp_1.write(
            {
                'with_foil': True,
                'unit_cost': 1,
            }
        )
        self.PackageConfiguratorStamp.create(
            {
                'configurator_id': self.cfg_1.id,
                'component_id': self.comp_base_greyboard.id,
                'stamp_id': self.stamp_1.id,
                'side': 'inside',
            }
        )
        # WHEN
        circ = self.PackageConfiguratorCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # THEN
        # Only 1 item expected.
        circ_item = circ.item_ids[0]
        # 50 + 4 = fixed cost + 1 * 4 quantity
        self.assertEqual(circ_item.stamp_cost, 54)
        self.assertAlmostEqual(circ.unit_cost, 0.54)
        self.assertEqual(circ.total_cost, 54)

    def test_04_cfg_box_stamp_cost_with_setup_n_with_foil(self):
        # GIVEN
        self.stamp_1.write(
            {
                'with_foil': True,
                'unit_cost': 0.1,
            }
        )
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
        self.PackageConfiguratorStamp.create(
            [
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'stamp_id': self.stamp_1.id,
                    'side': 'inside',
                },
                {
                    'configurator_id': self.cfg_1.id,
                    'component_id': self.comp_base_greyboard.id,
                    'stamp_id': self.stamp_1.id,
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
        self.assertEqual(circ_item.stamp_cost, 101)
        self.assertEqual(circ.unit_cost, 1.01)
        self.assertEqual(circ.total_cost, 101)
