from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..utils import generate_name_get


class MachineTag(models.Model):
    """Model to segment machines by tags."""

    _name = 'machine.tag'
    _description = 'Machine Instance Tag'

    name = fields.Char(required=True)
    parent_id = fields.Many2one('machine.tag', "Parent Tag")
    color = fields.Integer(string='Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

    @api.one
    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(
                _('Error! You cannot create recursive tags.'))

    @api.depends('name', 'parent_id.name')
    def name_get(self):
        """Override to show custom display_name."""
        return generate_name_get('{parent_id.name} / {name}', self)
