from ..value_objects.layout import BaseDimensions, Layout2D, LidDimensions
from . import common


class TestPackageBoxLayout(common.TestProductPackageConfiguratorCommon):
    def test_01_get_layouts(self):
        # GIVEN
        base_dimensions = BaseDimensions(
            length=165,
            width=42,
            height=14.5,
            outside_wrapping_extra=20,
        )
        lid_dimensions = LidDimensions(
            # TODO: should it be possible to have bigger height on lid
            # than on base?..
            height=16,
            thickness=1.5,
            extra=2,
        )
        # WHEN
        res = self.PackageBoxLayout.get_layouts(base_dimensions, lid_dimensions)
        # THEN
        self.assertEqual(
            res,
            {
                'base': {
                    'box': Layout2D(length=194, width=71),
                    'inside_wrapping': Layout2D(length=194, width=71),
                    'outside_wrapping': Layout2D(length=234, width=111),
                },
                'lid': {
                    'box': Layout2D(length=202, width=79),
                    'inside_wrapping': Layout2D(length=202, width=79),
                    'outside_wrapping': Layout2D(length=242, width=119),
                },
            },
        )
