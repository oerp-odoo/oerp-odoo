from odoo import models

from ..value_objects import layout as vo_layout


class PackageBoxLayout(models.AbstractModel):
    """Service to calculate layout for base, lid and their wrapping papers."""

    _name = 'package.box.layout'
    _description = "Package Box Layout"

    def get_cfg_layouts(self, cfg):
        # This is not change'able directly on configurator on purpose!
        global_extra = cfg.company_id.package_default_global_box_extra
        components = cfg.mapped('component_ids')
        comp_base_greyboard = components.filtered(
            lambda r: r.component_type == 'base_greyboard'
        )
        return self.get_layouts(
            vo_layout.BaseDimensions(
                length=cfg.base_length,
                width=cfg.base_width,
                height=cfg.base_height,
                outside_wrapping_extra=cfg.outside_wrapping_extra,
                extra=global_extra,
            ),
            vo_layout.LidDimensions(
                height=cfg.lid_height,
                # Lid greyboard depends on base greyboard thickness!
                thickness=comp_base_greyboard.sheet_id.sheet_type_id.thickness,
                extra=cfg.lid_extra + global_extra,
            ),
        )

    def get_layouts(
        self,
        base_dimensions: vo_layout.BaseDimensions,
        lid_dimensions: vo_layout.LidDimensions,
    ) -> dict:
        """Get 2D layouts from 3D dimensions."""
        if (
            not base_dimensions.length
            or not base_dimensions.width
            or not base_dimensions.height
        ):
            layout_zero = vo_layout.Layout2D(length=0.0, width=0.0)
            return {
                'base_greyboard': layout_zero,
                'base_wrappingpaper_inside': layout_zero,
                'base_wrappingpaper_outside': layout_zero,
                'lid_greyboard': layout_zero,
                'lid_wrappingpaper_inside': layout_zero,
                'lid_wrappingpaper_outside': layout_zero,
            }
        base_layout = self._get_base_layout(base_dimensions)
        lid_layout = self._get_lid_layout(base_dimensions, lid_dimensions)
        # Multiply by 2 for each side.
        wrapping_extra = base_dimensions.outside_wrapping_extra * 2
        return {
            'base_greyboard': base_layout,
            'base_wrappingpaper_inside': self._get_inside_wrapping_layout(base_layout),
            'base_wrappingpaper_outside': self._get_outside_wrapping_layout(
                base_layout,
                wrapping_extra,
            ),
            'lid_greyboard': lid_layout,
            'lid_wrappingpaper_inside': self._get_inside_wrapping_layout(lid_layout),
            'lid_wrappingpaper_outside': self._get_outside_wrapping_layout(
                lid_layout,
                wrapping_extra,
            ),
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
