from odoo import api, fields, models

from .. import const
from ..utils.lamination import calc_area_and_price
from ..value_objects import layout as vo_layout


# TODO: move to utils/component.py?
def get_comps(comps, *comp_types):
    def filter_comps(comps, ctype):
        return comps.filtered(lambda r: r.component_type == ctype)

    res = []
    for ctype in comp_types:
        comp = filter_comps(comps, ctype)
        # Adding even if there is no comp found, to make it more
        # flexible.
        res.append(comp)
    return res


class PackageConfiguratorBoxLamination(models.Model):
    _name = 'package.configurator.box.lamination'
    _description = "Package Configurator Box Lamination"

    configurator_id = fields.Many2one(
        'package.configurator.box', required=True, ondelete='cascade'
    )
    side = fields.Selection(
        const.COMPONENT_SIDE_SELECTION,
        default=const.ComponentSide.INSIDE,
        required=True,
    )
    lamination_id = fields.Many2one('package.lamination', required=True)
    area = fields.Float(compute='_compute_lamination_fields')
    area_unit_cost = fields.Float(
        compute='_compute_lamination_fields', help="Cost for single 'Unit' of Area"
    )

    @property
    def _area_data(self):
        self.ensure_one()
        # To handle cases before record is saved.
        side = self.side
        if not side or not self.lamination_id:
            return {'area': 0, 'area_unit_cost': 0}
        comps = self.configurator_id.component_ids
        (
            comp_base_wrappingpaper_side,
            comp_lid_wrappingpaper_side,
        ) = get_comps(comps, f'base_wrappingpaper_{side}', f'lid_wrappingpaper_{side}')
        res = calc_area_and_price(
            vo_layout.Layout2D(
                length=comp_base_wrappingpaper_side.component_length,
                width=comp_base_wrappingpaper_side.component_width,
            ).area,
            vo_layout.Layout2D(
                length=comp_lid_wrappingpaper_side.component_length,
                width=comp_lid_wrappingpaper_side.component_width,
            ).area,
            self.lamination_id.unit_cost,
        )
        return {'area': res['area'], 'area_unit_cost': res['price']}

    @api.depends(
        'configurator_id.component_ids.component_type',
        'configurator_id.component_ids.component_length',
        'configurator_id.component_ids.component_width',
        'side',
        'lamination_id',
    )
    def _compute_lamination_fields(self):
        for rec in self:
            rec.update(rec._area_data)
