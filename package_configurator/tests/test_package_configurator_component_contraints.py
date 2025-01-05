from odoo.exceptions import ValidationError

from . import common


class TestPackageConfiguratorComponentConstraints(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )

    def test_01_box_component_duplicate_part(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Component types must be unique per configurator!"
        ):
            self.PackageConfiguratorComponent.create(
                [
                    {
                        'component_type_id': self.component_type_base.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                    {
                        'component_type_id': self.component_type_base.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_02_box_component_kind_mismatch_sheet_type(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Kind mismatch\. It must match between component options!",
        ):
            self.PackageConfiguratorComponent.create(
                [
                    {
                        'component_type_id': self.component_type_base.id,
                        'sheet_type_id': self.package_sheet_type_wrappingpaper_1.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_03_box_component_kind_mismatch_sheet(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Kind mismatch\. It must match between component options!",
        ):
            self.PackageConfiguratorComponent.create(
                [
                    {
                        'component_type_id': self.component_type_base.id,
                        'sheet_id': self.package_sheet_wrappingpaper_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_04_box_component_missing_base(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, r"Base component is required!"):
            self.PackageConfiguratorComponent.create(
                [
                    {
                        'component_type_id': self.component_type_lid.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )

    def test_05_box_component_not_missing_base_multi(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        # WHEN, THEN
        try:
            self.PackageConfiguratorComponent.create(
                [
                    {
                        'component_type_id': self.component_type_lid.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                    {
                        'component_type_id': self.component_type_base.id,
                        'sheet_id': self.package_sheet_greyboard_1.id,
                        'configurator_id': cfg.id,
                    },
                ]
            )
        except ValidationError as e:
            self.fail(f"base is created, so it should pass. Error: {e}")

    def test_06_box_component_not_missing_base_single(self):
        # GIVEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                'base_length': 165,
                'base_width': 42,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        self.PackageConfiguratorComponent.create(
            {
                'component_type_id': self.component_type_base.id,
                'sheet_id': self.package_sheet_greyboard_1.id,
                'configurator_id': cfg.id,
            }
        )
        # WHEN, THEN
        try:
            self.PackageConfiguratorComponent.create(
                {
                    'component_type_id': self.component_type_lid.id,
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                }
            )
        except ValidationError as e:
            self.fail(f"base is created, so it should pass {e}")
