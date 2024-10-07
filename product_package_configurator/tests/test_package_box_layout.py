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
            extra=30,
        )
        lid_dimensions = LidDimensions(
            height=16,
            thickness=1.5,
            extra=32,
        )
        # WHEN
        res = self.PackageBoxLayout.get_layouts(base_dimensions, lid_dimensions)
        # THEN
        self.assertEqual(
            res,
            {
                'base': {
                    'box': Layout2D(length=224, width=101),
                    'inside_wrapping': Layout2D(length=224, width=101),
                    'outside_wrapping': Layout2D(length=264, width=141),
                },
                'lid': {
                    'box': Layout2D(length=232, width=109),
                    'inside_wrapping': Layout2D(length=232, width=109),
                    'outside_wrapping': Layout2D(length=272, width=149),
                },
            },
        )
