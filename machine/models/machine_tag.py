from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        def get_parent_name(parent):
            while parent.parent_id:
                parent = parent.parent_id
                yield parent.name

        res = []
        for rec in self:
            # Include current record name.
            names = [rec.name]
            for parent_name in get_parent_name(rec):
                names.append(parent_name)
            # We reverse names list, because we display most parent
            # names first.
            res.append((rec.id, ' / '.join(reversed(names))))
        return res
