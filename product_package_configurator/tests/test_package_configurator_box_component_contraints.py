from odoo.exceptions import ValidationError

from . import common


class TestPackageConfiguratorBoxComponentConstraints(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})

    def test_01_box_component_duplicate_part(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'sheet_greyboard_base_id': self.package_sheet_greyboard_1.id,
                'sheet_greyboard_lid_id': self.package_sheet_greyboard_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Component types must be unique per configurator!"
        ):
            self.PackageConfiguratorBoxComponentType.create(
                [
                    {
                        'component_type': 'base_greyboard',
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                    {
                        'component_type': 'base_greyboard',
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_02_box_component_scope_mismatch_sheet_type(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'sheet_greyboard_base_id': self.package_sheet_greyboard_1.id,
                'sheet_greyboard_lid_id': self.package_sheet_greyboard_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Scope mismatch\. Scope must match between component options!",
        ):
            self.PackageConfiguratorBoxComponentType.create(
                [
                    {
                        'component_type': 'base_greyboard',
                        'sheet_type_id': self.package_sheet_type_wrappingpaper_1.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_03_box_component_scope_mismatch_sheet(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                # thickness: 1.5mm
                'sheet_greyboard_base_id': self.package_sheet_greyboard_1.id,
                'sheet_greyboard_lid_id': self.package_sheet_greyboard_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Scope mismatch\. Scope must match between component options!",
        ):
            self.PackageConfiguratorBoxComponentType.create(
                [
                    {
                        'component_type': 'base_greyboard',
                        'sheet_id': self.package_sheet_wrappingpaper_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )
