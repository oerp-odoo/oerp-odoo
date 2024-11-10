from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const, utils
from ..value_objects import layout as vo_layout

MANDATORY_LAYOUT_INP_FIELDS = [
    'base_length',
    'base_width',
    'base_height',
    'lid_height',
]


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


class PackageConfiguratorBox(models.Model):
    _name = 'package.configurator.box'
    _inherit = 'package.configurator'
    _description = "Box Configurator"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if res.get('company_id'):
            company = self.env['res.company'].browse(res['company_id'])
        else:
            company = self.env.company
        if 'lid_extra' in default_fields:
            res['lid_extra'] = company.package_default_lid_extra
        if 'outside_wrapping_extra' in default_fields:
            res[
                'outside_wrapping_extra'
            ] = company.package_default_outside_wrapping_extra
        return res

    component_ids = fields.One2many(
        comodel_name='package.configurator.box.component',
        inverse_name='configurator_id',
        string="Components",
    )
    circulation_ids = fields.One2many(
        comodel_name='package.configurator.box.circulation'
    )
    lid_height = fields.Float(required=True)
    lid_extra = fields.Float()
    outside_wrapping_extra = fields.Float()
    box_type_id = fields.Many2one('package.box.type', required=True)
    # Sheets
    sheet_greyboard_base_id = fields.Many2one(
        'package.sheet',
        string="Base Grey Board",
        required=False,
        domain=[('scope', '=', const.SheetTypeScope.GREYBOARD)],
    )
    sheet_greyboard_lid_id = fields.Many2one(
        'package.sheet',
        string="Lid Grey Board",
        domain=[('scope', '=', const.SheetTypeScope.GREYBOARD)],
    )
    sheet_wrappingpaper_base_outside_id = fields.Many2one(
        'package.sheet',
        string="Base Outside Wrapping Paper",
        domain=[('scope', '=', const.SheetTypeScope.WRAPPINGPAPER)],
    )
    sheet_wrappingpaper_base_inside_id = fields.Many2one(
        'package.sheet',
        string="Base Inside Wrapping Paper",
        domain=[('scope', '=', const.SheetTypeScope.WRAPPINGPAPER)],
    )
    sheet_wrappingpaper_lid_outside_id = fields.Many2one(
        'package.sheet',
        string="Lid Outside Wrapping Paper",
        domain=[('scope', '=', const.SheetTypeScope.WRAPPINGPAPER)],
    )
    sheet_wrappingpaper_lid_inside_id = fields.Many2one(
        'package.sheet',
        string="Lid Inside Wrapping Paper",
        domain=[('scope', '=', const.SheetTypeScope.WRAPPINGPAPER)],
    )
    lamination_outside_id = fields.Many2one(
        'package.lamination',
        string="Outside Lamination",
    )
    lamination_inside_id = fields.Many2one(
        'package.lamination', string="Inside Lamination"
    )
    # Base
    base_layout_length = fields.Float(compute='_compute_layouts_data')
    base_layout_width = fields.Float(compute='_compute_layouts_data')
    base_inside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    base_inside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    base_outside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    base_outside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    # Lid
    lid_layout_length = fields.Float(compute='_compute_layouts_data')
    lid_layout_width = fields.Float(compute='_compute_layouts_data')
    lid_inside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    lid_inside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    lid_outside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    lid_outside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    # Lamination
    lamination_inside_area = fields.Float(compute='_compute_lamination_fields')
    lamination_inside_unit_cost = fields.Float(compute='_compute_lamination_fields')
    lamination_outside_area = fields.Float(compute='_compute_lamination_fields')
    lamination_outside_unit_cost = fields.Float(compute='_compute_lamination_fields')

    @api.depends(
        'sheet_greyboard_base_id',
        'base_length',
        'base_width',
        'base_height',
        'lid_height',
        'lid_extra',
        'outside_wrapping_extra',
    )
    def _compute_layouts_data(self):
        for rec in self:
            if all(rec[fname] for fname in MANDATORY_LAYOUT_INP_FIELDS):
                rec.update(rec._get_layouts_data())
            else:
                rec.update(rec._get_init_layouts_data())

    # Move lamination logic to package.configurator.box.component!
    @api.depends(
        'lamination_outside_id',
        'lamination_inside_id',
        'base_inside_wrapping_length',
        'base_inside_wrapping_width',
        'base_outside_wrapping_length',
        'base_outside_wrapping_width',
        'lid_inside_wrapping_length',
        'lid_inside_wrapping_width',
        'lid_outside_wrapping_length',
        'lid_outside_wrapping_width',
        'component_ids.component_type',
        'component_ids.component_length',
        'component_ids.component_width',
        'base_length',
        'base_width',
        'base_height',
        'lid_height',
    )
    def _compute_lamination_fields(self):
        calc_area_and_price = utils.lamination.calc_area_and_price
        for box in self:
            data = box._get_init_laminations_data()
            comps = box.component_ids
            if box.lamination_inside_id:
                (
                    comp_base_wrappingpaper_inside,
                    comp_lid_wrappingpaper_inside,
                ) = get_comps(
                    comps, 'base_wrappingpaper_inside', 'lid_wrappingpaper_inside'
                )
                res = calc_area_and_price(
                    vo_layout.Layout2D(
                        length=comp_base_wrappingpaper_inside.component_length,
                        width=comp_base_wrappingpaper_inside.component_width,
                    ).area,
                    vo_layout.Layout2D(
                        length=comp_lid_wrappingpaper_inside.component_length,
                        width=comp_lid_wrappingpaper_inside.component_width,
                    ).area,
                    box.lamination_inside_id.unit_cost,
                )
                data.update(
                    {
                        'lamination_inside_area': res['area'],
                        'lamination_inside_unit_cost': res['price'],
                    }
                )
            if box.lamination_outside_id:
                (
                    comp_base_wrappingpaper_outside,
                    comp_lid_wrappingpaper_outside,
                ) = get_comps(
                    comps, 'base_wrappingpaper_outside', 'lid_wrappingpaper_outside'
                )
                res = calc_area_and_price(
                    vo_layout.Layout2D(
                        length=comp_base_wrappingpaper_outside.component_length,
                        width=comp_base_wrappingpaper_outside.component_width,
                    ).area,
                    vo_layout.Layout2D(
                        length=comp_lid_wrappingpaper_outside.component_length,
                        width=comp_lid_wrappingpaper_outside.component_width,
                    ).area,
                    box.lamination_outside_id.unit_cost,
                )
                data.update(
                    {
                        'lamination_outside_area': res['area'],
                        'lamination_outside_unit_cost': res['price'],
                    }
                )
            box.update(data)

    @api.constrains(
        'box_type_id',
        'base_length',
        'base_width',
        'base_height',
    )
    def _check_dimensions(self):
        def get_msg(name, dim_type, min_amount):
            return _(
                "Minimum box (%(name)s) %(dim_type)s is %(min_amount)s",
                name=name,
                dim_type=dim_type,
                min_amount=min_amount,
            )

        for box in self:
            res = box.box_type_id.validate_dimensions(
                box.base_length, box.base_width, box.base_height
            )
            box_type = box.box_type_id
            name = box_type.name
            if not res['length']:
                raise ValidationError(get_msg(name, _("length"), box_type.min_length))
            if not res['width']:
                raise ValidationError(get_msg(name, _("width"), box_type.min_width))
            if not res['height']:
                raise ValidationError(get_msg(name, _("height"), box_type.min_height))

    def action_setup(self):
        """Create/recreate setup records for each circulation."""
        self.ensure_one()
        self.circulation_ids.create_circulation_setups(self._find_box_setups())
        return True

    def _find_box_setups(self):
        # TODO: we might need to search different type of setups separately, when
        # we will have more than one type!
        return self.env['package.box.setup'].search(
            [('company_id', '=', self.company_id.id)]
        )

    def _get_layouts_data(self):
        self.ensure_one()
        # This is not change'able directly on configurator on
        # purpose!
        # TODO: move layout data calculation to component model!
        global_extra = self.company_id.package_default_global_box_extra
        res = self.env['package.box.layout'].get_layouts(
            vo_layout.BaseDimensions(
                length=self.base_length,
                width=self.base_width,
                height=self.base_height,
                outside_wrapping_extra=self.outside_wrapping_extra,
                extra=global_extra,
            ),
            vo_layout.LidDimensions(
                height=self.lid_height,
                thickness=self.sheet_greyboard_base_id.sheet_type_id.thickness,
                extra=self.lid_extra + global_extra,
            ),
        )
        return {
            'base_layout_length': res['base']['box'].length,
            'base_layout_width': res['base']['box'].width,
            'base_inside_wrapping_length': res['base']['inside_wrapping'].length,
            'base_inside_wrapping_width': res['base']['inside_wrapping'].width,
            'base_outside_wrapping_length': res['base']['outside_wrapping'].length,
            'base_outside_wrapping_width': res['base']['outside_wrapping'].width,
            'lid_layout_length': res['lid']['box'].length,
            'lid_layout_width': res['lid']['box'].width,
            'lid_inside_wrapping_length': res['lid']['inside_wrapping'].length,
            'lid_inside_wrapping_width': res['lid']['inside_wrapping'].width,
            'lid_outside_wrapping_length': res['lid']['outside_wrapping'].length,
            'lid_outside_wrapping_width': res['lid']['outside_wrapping'].width,
        }

    def _get_init_layouts_data(self):
        self.ensure_one()
        return {
            'base_layout_length': 0.0,
            'base_layout_width': 0.0,
            'base_inside_wrapping_length': 0.0,
            'base_inside_wrapping_width': 0.0,
            'base_outside_wrapping_length': 0.0,
            'base_outside_wrapping_width': 0.0,
            'lid_layout_length': 0.0,
            'lid_layout_width': 0.0,
            'lid_inside_wrapping_length': 0.0,
            'lid_inside_wrapping_width': 0.0,
            'lid_outside_wrapping_length': 0.0,
            'lid_outside_wrapping_width': 0.0,
        }

    def _get_init_laminations_data(self):
        return {
            'lamination_inside_area': 0,
            'lamination_inside_unit_cost': 0,
            'lamination_outside_area': 0,
            'lamination_outside_unit_cost': 0,
        }

    def _get_init_fit_qty_data(self):
        return {
            'base_layout_fit_qty': 0,
            'base_inside_fit_qty': 0,
            'base_outside_fit_qty': 0,
            'lid_layout_fit_qty': 0,
            'lid_inside_fit_qty': 0,
            'lid_outside_fit_qty': 0,
        }
