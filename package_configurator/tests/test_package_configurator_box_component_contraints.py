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
            self.PackageConfiguratorBoxComponent.create(
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
            self.PackageConfiguratorBoxComponent.create(
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
            self.PackageConfiguratorBoxComponent.create(
                [
                    {
                        'component_type': 'base_greyboard',
                        'sheet_id': self.package_sheet_wrappingpaper_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_04_box_component_missing_base_greyboard(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
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
            ValidationError, r"Base Greyboard component is required!"
        ):
            self.PackageConfiguratorBoxComponent.create(
                [
                    {
                        'component_type': 'lid_greyboard',
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_05_box_component_not_missing_base_greyboard_multi(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        # WHEN, THEN
        try:
            self.PackageConfiguratorBoxComponent.create(
                [
                    {
                        'component_type': 'lid_greyboard',
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
        except ValidationError as e:
            self.fail(f"base_greyboard is created, so it should pass. Error: {e}")

    def test_06_box_component_not_missing_base_greyboard_single(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            }
        )
        self.PackageConfiguratorBoxComponent.create(
            {
                'component_type': 'base_greyboard',
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            }
        )
        # WHEN, THEN
        try:
            self.PackageConfiguratorBoxComponent.create(
                {
                    'component_type': 'lid_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                }
            )
        except ValidationError as e:
            self.fail(f"base_greyboard is created, so it should pass {e}")
