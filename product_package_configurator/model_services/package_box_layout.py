import dataclasses

from odoo import models


@dataclasses.dataclass(frozen=True, kw_only=True)
class BaseDimensions:
    length: float  # mm
    width: float
    height: float
    outside_wrapping_extra: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class LidDimensions:
    height: float
    thickness: float
    # To make it slightly bigger than base so it would fit on it.
    extra: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class Layout:
    """Package layout on 2D plane."""

    length: float  # mm
    width: float

    @property
    def area(self):
        return self.length * self.width


class PackageBoxLayout(models.AbstractModel):
    """Service to calculate layout for base, lid and their wrapping papers."""

    _name = 'package.box.layout'
    _description = "Package Box Layout"

    # TODO: Lid dimensions should be optional.
    def get_layouts(
        self,
        base_dimensions: BaseDimensions,
        lid_dimensions: LidDimensions,
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

    def _get_base_layout(self, dimensions: BaseDimensions) -> Layout:
        height_converted = self._convert_height(dimensions.height)
        return Layout(
            length=dimensions.length + height_converted,
            width=dimensions.width + height_converted,
        )

    def _get_lid_layout(
        self, base_dimensions: BaseDimensions, lid_dimensions: LidDimensions
    ) -> Layout:
        height_converted = self._convert_height(lid_dimensions.height)
        # Should we always multiply it by 2?..
        thickness = lid_dimensions.thickness * 2
        all_extras = thickness + lid_dimensions.extra + height_converted
        return Layout(
            length=base_dimensions.length + all_extras,
            width=base_dimensions.width + all_extras,
        )

    def _get_inside_wrapping_layout(self, layout: Layout):
        # Inside wrapping matches provided layout! Though creating new
        # object to make sure they are actually different entities!
        return Layout(length=layout.length, width=layout.width)

    def _get_outside_wrapping_layout(self, layout: Layout, extra: float):
        return Layout(length=layout.length + extra, width=layout.width + extra)

    def _convert_height(self, height: float):
        """Convert height amount for 2D plane."""
        return 2 * height
