from footil.formatting import generate_names

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ApilogLabel(models.Model):
    _name = 'apilog.label'
    _description = "API Log Label"

    name = fields.Char(required=True)
    code = fields.Char()
    parent_id = fields.Many2one('apilog.label')

    _name_uniq = models.Constraint(
        'unique(name)',
        'The Name must be unique!',
    )
    _code_uniq = models.Constraint(
        'unique(code)',
        'The Code must be unique!',
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        for label in self:
            if not label._check_recursion():
                raise ValidationError(_("Error! You cannot create recursive labels!"))

    def name_get(self):
        """Override to display names hierarchy."""
        return generate_names(
            {
                'pattern': ('$join_parent_attrs("parent_id", "name", " / ", "True")'),
                'strip_falsy': True,
                'objects': self,
            }
        )
