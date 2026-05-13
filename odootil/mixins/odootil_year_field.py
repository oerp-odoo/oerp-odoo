from footil.date import to_date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

DT = fields.Date


class OdootilYearField(models.AbstractModel):
    """Mixin adds odootil_year field with constraint, default value."""

    _name = 'odootil.year_field'
    _description = 'Odootil Year Field Mixin'

    @api.model
    def default_get(self, fields):
        """Override to include current year as default odootil_year."""
        res = super().default_get(fields)
        res['odootil_year'] = str(DT.to_date(DT.context_today(self)).year)
        return res

    odootil_year = fields.Char("Year", size=4)

    @api.constrains('odootil_year')
    def check_odootil_year(self):
        """Check if entered odootil_year field is valid."""
        for rec in self:
            year = rec.odootil_year
            try:
                to_date(year, fmt='%Y')
            except ValueError:
                raise ValidationError(_("%s is not valid year!") % year)
