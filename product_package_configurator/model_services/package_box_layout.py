from odoo import models

from ..value_objects import layout as vo_layout


class PackageBoxLayout(models.AbstractModel):
    """Service to calculate layout for base, lid and their wrapping papers."""

    _name = 'package.box.layout'
    _description = "Package Box Layout"

    # TODO: Lid dimensions should be optional.
    def get_layouts(
        self,
        base_dimensions: vo_layout.BaseDimensions,
        lid_dimensions: vo_layout.LidDimensions,
    ) -> dict:
        """Get 2D layouts from 3D dimensions."""
        base_layout = self._get_base_layout(base_dimensions)
        lid_layout = self._get_lid_layout(base_dimensions, lid_dimensions)
        # Multiply by 2 for each side.
        wrapping_extra = base_dimensions.outside_wrapping_extra * 2
        return {
            'base': {
                'box': base_layout,
                'inside_wrapping': self._get_inside_wrapping_layout(base_layout),
                'outside_wrapping': self._get_outside_wrapping_layout(
                    base_layout,
                    wrapping_extra,
                ),
            },
            'lid': {
                'box': lid_layout,
                'inside_wrapping': self._get_inside_wrapping_layout(lid_layout),
                'outside_wrapping': self._get_outside_wrapping_layout(
                    lid_layout,
                    wrapping_extra,
                ),
            },
        }

    def _get_base_layout(
        self, dimensions: vo_layout.BaseDimensions
    ) -> vo_layout.Layout2D:
        height_converted = self._convert_height(dimensions.height)
        extra = dimensions.extra
        return vo_layout.Layout2D(
            length=dimensions.length + height_converted + extra,
            width=dimensions.width + height_converted + extra,
        )

    def _get_lid_layout(
        self,
        base_dimensions: vo_layout.BaseDimensions,
        lid_dimensions: vo_layout.LidDimensions,
    ) -> vo_layout.Layout2D:
        height_converted = self._convert_height(lid_dimensions.height)
        # Should we always multiply it by 2?..
        thickness = lid_dimensions.thickness * 2
        all_extras = thickness + lid_dimensions.extra + height_converted
        return vo_layout.Layout2D(
            length=base_dimensions.length + all_extras,
            width=base_dimensions.width + all_extras,
        )

    def _get_inside_wrapping_layout(self, layout: vo_layout.Layout2D):
        # Inside wrapping matches provided layout! Though creating new
        # object to make sure they are actually different entities!
        return vo_layout.Layout2D(length=layout.length, width=layout.width)

    def _get_outside_wrapping_layout(self, layout: vo_layout.Layout2D, extra: float):
        return vo_layout.Layout2D(
            length=layout.length + extra, width=layout.width + extra
        )

    def _convert_height(self, height: float):
        """Convert height amount for 2D plane."""
        return 2 * height
