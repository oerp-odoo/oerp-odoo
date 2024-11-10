from odoo import fields, models

HELP_MIN_MSG = "0 means, there is no constraint"


class PackageBoxType(models.Model):
    """Model to specify box type."""

    _name = 'package.box.type'
    _description = "Package Box Type"

    name = fields.Char(required=True)
    min_length = fields.Float("Minimum Length (mm)", help=HELP_MIN_MSG)
    min_width = fields.Float("Minimum Width (mm)", help=HELP_MIN_MSG)
    min_height = fields.Float("Minimum Height (mm)", help=HELP_MIN_MSG)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    def validate_dimensions(self, length: float, width: float, height: float):
        self.ensure_one()
        return {
            'length': not self.min_length or self.min_length <= length,
            'width': not self.min_width or self.min_width <= width,
            'height': not self.min_height or self.min_height <= height,
        }
