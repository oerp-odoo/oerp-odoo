from odoo import fields, models

HELP_MIN_MSG = "0 means, there is no constraint"


class PackageKind(models.Model):
    """Model to specify package kind."""

    _name = 'package.kind'
    _description = "Package Kind"

    name = fields.Char(required=True)
    package_type_id = fields.Many2one('package.type', required=True)
    # TODO: this might only be applicable to box packages in a future.
    min_length = fields.Float("Minimum Length (mm)", help=HELP_MIN_MSG)
    min_width = fields.Float("Minimum Width (mm)", help=HELP_MIN_MSG)
    min_height = fields.Float("Minimum Height (mm)", help=HELP_MIN_MSG)
    default_component_ids = fields.Many2many(
        'package.default.component',
        'package_box_type_default_component_rel',
        'package_kind_id',
        'default_component_id',
        string="Default Components",
        help="Will be pre filled on configurator if no component was selected yet",
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    _sql_constraints = [
        (
            'name_package_type_company_uniq',
            'unique (name, package_type_id, company_id)',
            'The Name must be unique per Package Type and Company!',
        )
    ]

    def validate_dimensions(self, length: float, width: float, height: float):
        self.ensure_one()
        return {
            'length': not self.min_length or self.min_length <= length,
            'width': not self.min_width or self.min_width <= width,
            'height': not self.min_height or self.min_height <= height,
        }
