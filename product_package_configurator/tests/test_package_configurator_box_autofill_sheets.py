from .. import const
from . import common


class TestPackageConfiguratorBoxAutofillSheets(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})

    def test_01_configure_box_autofill_greyboard_lid(self):
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'sheet_greyboard_base_id': self.package_sheet_greyboard_1.id,
                'sheet_type_greyboard_lid_id': self.package_sheet_type_greyboard_1.id,
                'sheet_greyboard_lid_id': False,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        cfg._compute_sheet_greyboard_lid_id()
        # THEN
        self.assertEqual(cfg.sheet_greyboard_lid_id, self.package_sheet_greyboard_1)

    def test_02_configure_box_not_autofill_greyboard_lid(self):
        # GIVEN
        package_sheet_greyboard_2 = self.PackageSheet.create(
            {
                'sheet_type_id': self.package_sheet_type_greyboard_1.id,
                'sheet_length': 1000,
                'sheet_width': 700,
                'unit_cost': 0.05,
                'scope': const.SheetTypeScope.GREYBOARD,
            }
        )
        # WHEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'sheet_greyboard_base_id': self.package_sheet_greyboard_1.id,
                'sheet_type_greyboard_lid_id': self.package_sheet_type_greyboard_1.id,
                'sheet_greyboard_lid_id': package_sheet_greyboard_2.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        cfg._compute_sheet_greyboard_lid_id()
        # THEN
        self.assertEqual(cfg.sheet_greyboard_lid_id, package_sheet_greyboard_2)
