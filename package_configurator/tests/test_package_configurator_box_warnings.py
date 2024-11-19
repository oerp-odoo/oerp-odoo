from ..value_objects import package_warning as vo_pw
from . import common


class TestPackageConfiguratorBoxWarnings(common.TestProductPackageConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package_box_type_1 = cls.PackageBoxType.create({'name': 'MY-BOX-TYPE-1'})

    def test_01_configure_box_warning_box_component_not_fitting_on_sheet(self):
        # GIVEN
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 10000,
                'base_width': 10000,
                'base_height': 10000,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            },
        )
        self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # WHEN
        warnings = cfg.get_warnings()
        # THEN
        self.assertEqual(
            warnings,
            [
                vo_pw.PackageWarning(
                    warning_type=vo_pw.WarningType.DANGER,
                    message='Component "Base Grey Board" won\'t fit on sheet '
                    + f'{self.package_sheet_greyboard_1.display_name}',
                )
            ],
        )

    def test_02_configure_box_warning_missing_default_components(self):
        # GIVEN
        self.package_box_type_1.default_component_ids |= (
            self.PackageDefaultComponent.create({'component_type': 'lid_greyboard'})
        )
        cfg = self.PackageConfiguratorBox.create(
            {
                'box_type_id': self.package_box_type_1.id,
                'base_length': 1,
                'base_width': 1,
                'base_height': 1,
                'lid_height': 16,
                'lid_extra': 2.0,
                'outside_wrapping_extra': 20.0,
            },
        )
        self.PackageConfiguratorBoxComponent.create(
            [
                {
                    'component_type': 'base_greyboard',
                    'sheet_id': self.package_sheet_greyboard_1.id,
                    'configurator_id': cfg.id,
                },
            ]
        )
        # WHEN
        warnings = cfg.get_warnings()
        # THEN
        self.assertEqual(
            warnings,
            [
                vo_pw.PackageWarning(
                    warning_type=vo_pw.WarningType.WARNING,
                    message=(
                        'Expected default components not used: '
                        + '<strong>Lid Grey Board</strong>'
                    ),
                )
            ],
        )
