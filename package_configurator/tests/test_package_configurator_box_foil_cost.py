from .. import const
from . import common


class TestPackageConfiguratorBoxFoilCost(common.TestProductPackageConfiguratorCommon):
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
                'scope': const.SheetTypeScope.GREYBOARD,
            }
        )
        cls.cfg_1 = cls.PackageConfiguratorBox.create(
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
        cls.comp_base_greyboard = cls.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': cls.package_sheet_1.id,
                'configurator_id': cls.cfg_1.id,
            },
        )

    def test_01_cfg_box_foil_cost_single_foil(self):
        # GIVEN
        circ = self.PackageConfiguratorBoxCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        self.PackageConfiguratorBoxFoil.create(
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
        # 50 + 0.1 * 100
        self.assertEqual(circ_item.foil_cost, 60)
        self.assertEqual(circ.unit_cost, 0.6)
        self.assertEqual(circ.total_cost, 60)

    def test_02_cfg_box_foil_cost_two_foils(self):
        # GIVEN
        circ = self.PackageConfiguratorBoxCirculation.create(
            {'quantity': 100, 'configurator_id': self.cfg_1.id},
        )
        # WHEN
        self.PackageConfiguratorBoxFoil.create(
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
        # (50 + 0.1 * 100) + (50 + 0.1 * 100)
        self.assertEqual(circ_item.foil_cost, 120)
        self.assertEqual(circ.unit_cost, 1.2)
        self.assertEqual(circ.total_cost, 120)
