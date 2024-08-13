from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const
from ..model_services.package_box_layout import BaseDimensions, LidDimensions

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

    lid_height = fields.Float(required=True)
    lid_thickness = fields.Float(default=const.DEFAULT_LID_THICKNESS)
    lid_extra = fields.Float(default=const.DEFAULT_LID_EXTRA)
    outside_wrapping_extra = fields.Float(default=const.DEFAULT_OUTSIDE_WRAPPING_EXTRA)
    box_type_id = fields.Many2one('package.box.type', required=True)
    base_layout_length = fields.Float(compute='_compute_layouts_data')
    base_layout_width = fields.Float(compute='_compute_layouts_data')
    base_inside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    base_inside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    base_outside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    base_outside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    lid_layout_length = fields.Float(compute='_compute_layouts_data')
    lid_layout_width = fields.Float(compute='_compute_layouts_data')
    lid_inside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    lid_inside_wrapping_width = fields.Float(compute='_compute_layouts_data')
    lid_outside_wrapping_length = fields.Float(compute='_compute_layouts_data')
    lid_outside_wrapping_width = fields.Float(compute='_compute_layouts_data')

    @api.depends(
        'base_length',
        'base_width',
        'base_height',
        'lid_height',
        'lid_thickness',
        'lid_extra',
        'outside_wrapping_extra',
    )
    def _compute_layouts_data(self):
        for rec in self:
            if all(rec[fname] for fname in MANDATORY_LAYOUT_INP_FIELDS):
                rec.update(rec._get_layouts_data())
            else:
                rec.update(rec._get_init_layouts_data())

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
        res = self.env['package.box.layout'].get_layouts(
            BaseDimensions(
                length=self.base_length,
                width=self.base_width,
                height=self.base_height,
                outside_wrapping_extra=self.outside_wrapping_extra,
            ),
            LidDimensions(
                height=self.lid_height,
                thickness=self.lid_thickness,
                extra=self.lid_extra,
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
