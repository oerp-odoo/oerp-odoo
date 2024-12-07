from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PackageAreaRangeMixin(models.AbstractModel):
    _name = 'package.area.range.mixin'
    _description = "Package Area Range Mixin"

    area_range_name = fields.Char(compute='_compute_area_range_name')
    area_range_from_id = fields.Many2one('package.area', string="Area From")
    area_range_to_id = fields.Many2one('package.area', string="Area To")

    @api.depends('area_range_from_id', 'area_range_to_id')
    def _compute_area_range_name(self):
        for rec in self:
            from_name = rec.area_range_from_id.name
            to_name = rec.area_range_to_id.name
            if from_name and to_name:
                rec.area_range_name = f'{from_name} - {to_name}'
            elif from_name:
                rec.area_range_name = f'>{from_name}'
            else:
                rec.area_range_name = f'<{to_name}'

    @api.constrains('area_range_from_id', 'area_range_to_id')
    def _check_area_range(self):
        for rec in self:
            if not rec.area_range_from_id and not rec.area_range_to_id:
                raise ValidationError(_("Must select at least Area From or Area To!"))
            if (
                rec.area_range_from_id
                and rec.area_range_to_id
                and rec.area_range_from_id == rec.area_range_to_id
            ):
                raise ValidationError(_("Area From and Area To must be different!"))
