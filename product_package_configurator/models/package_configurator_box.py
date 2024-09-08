from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import utils
from ..value_objects.layout import BaseDimensions, Layout2D, LidDimensions

MANDATORY_LAYOUT_INP_FIELDS = [
    'base_length',
    'base_width',
    'base_height',
    'lid_height',
]


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

    lid_height = fields.Float(required=True)
    lid_extra = fields.Float()
    outside_wrapping_extra = fields.Float()
    box_type_id = fields.Many2one('package.box.type', required=True)
    # Should we call it grayboard?
    carton_id = fields.Many2one('package.carton', required=True)
    lamination_outside_id = fields.Many2one(
        'package.lamination', string="Outside Lamination"
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
    lamination_inside_price = fields.Float(compute='_compute_lamination_fields')
    lamination_outside_area = fields.Float(compute='_compute_lamination_fields')
    lamination_outside_price = fields.Float(compute='_compute_lamination_fields')

    @api.depends(
        'carton_id',
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
    )
    def _compute_lamination_fields(self):
        calc_area_and_price = utils.lamination.calc_area_and_price
        for box in self:
            data = box._get_init_laminations_data()
            if box.lamination_inside_id:
                res = calc_area_and_price(
                    Layout2D(
                        length=box.base_inside_wrapping_length,
                        width=box.base_inside_wrapping_width,
                    ).area,
                    Layout2D(
                        length=box.lid_inside_wrapping_length,
                        width=box.lid_inside_wrapping_width,
                    ).area,
                    box.lamination_inside_id.price_unit,
                )
                data.update(
                    {
                        'lamination_inside_area': res['area'],
                        'lamination_inside_price': res['price'],
                    }
                )
            if box.lamination_outside_id:
                res = calc_area_and_price(
                    Layout2D(
                        length=box.base_outside_wrapping_length,
                        width=box.base_outside_wrapping_width,
                    ).area,
                    Layout2D(
                        length=box.lid_outside_wrapping_length,
                        width=box.lid_outside_wrapping_width,
                    ).area,
                    box.lamination_outside_id.price_unit,
                )
                data.update(
                    {
                        'lamination_outside_area': res['area'],
                        'lamination_outside_price': res['price'],
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

    def _get_layouts_data(self):
        self.ensure_one()
        # This is not change'able directly on configurator on
        # purpose!
        global_extra = self.company_id.package_default_global_box_extra
        res = self.env['package.box.layout'].get_layouts(
            BaseDimensions(
                length=self.base_length,
                width=self.base_width,
                height=self.base_height,
                outside_wrapping_extra=self.outside_wrapping_extra,
                extra=global_extra,
            ),
            LidDimensions(
                height=self.lid_height,
                thickness=self.carton_id.thickness,
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
            'lamination_inside_price': 0,
            'lamination_outside_area': 0,
            'lamination_outside_price': 0,
        }
