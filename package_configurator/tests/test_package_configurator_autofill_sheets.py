from odoo.tests.form import Form

from . import common


class TestPackageConfiguratorAutofillSheets(
    common.TestProductPackageConfiguratorCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_kind_box_1 = cls.PackageKind.create(
            {'name': 'MY-BOX-TYPE-1', 'package_type_id': cls.package_type_box.id}
        )

    def test_01_configure_box_autofill_base_greyboard(self):
        # WHEN
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
        ctx = {'default_configurator_id': cfg.id}
        with Form(self.PackageConfiguratorComponent.with_context(**ctx)) as comp:
            comp.component_type_id = self.component_type_base
            comp.sheet_type_id = self.package_sheet_type_greyboard_1
            # THEN
            self.assertEqual(comp.sheet_id, self.package_sheet_greyboard_1)

    def test_02_configure_box_not_autofill_base_greyboard(self):
        # WHEN
        cfg = self.PackageConfigurator.create(
            {
                'package_kind_id': self.package_kind_box_1.id,
                # Too big to fit.
                'base_length': 16500,
                'base_width': 4200,
                'base_height': 14.5,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
                'package_type_id': self.package_type_box.id,
            }
        )
        ctx = {'default_configurator_id': cfg.id}
        with Form(self.PackageConfiguratorComponent.with_context(**ctx)) as comp:
            comp.component_type_id = self.component_type_base
            comp.sheet_type_id = self.package_sheet_type_greyboard_1
            # THEN
            self.assertEqual(comp.sheet_id, self.PackageSheet)
            # Must set sheet_id, because when exiting, Form will try to save it and
            # will give error, because sheet_id is required.
            comp.sheet_id = self.package_sheet_greyboard_1
