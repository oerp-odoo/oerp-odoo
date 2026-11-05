from footil.formatting import generate_names

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ApilogLabel(models.Model):
    _name = 'apilog.label'
    _description = "API Log Label"

    name = fields.Char(required=True)
    code = fields.Char()
    parent_id = fields.Many2one('apilog.label')
    display_name = fields.Char(compute='_compute_display_name', recursive=True)

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
            if label._has_cycle():
                raise ValidationError(_("Error! You cannot create recursive labels!"))

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        """Display names hierarchy."""
        names = dict(
            generate_names(
                {
                    'pattern': (
                        '$join_parent_attrs("parent_id", "name", " / ", "True")'
                    ),
                    'strip_falsy': True,
                    'objects': self,
                }
            )
        )
        for label in self:
            label.display_name = names[label.id]
