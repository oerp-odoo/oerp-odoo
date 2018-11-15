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

    @api.multi
    @api.depends('name', 'parent_id')
    def name_get(self):
        """Override to show parent_id name if one is set."""
        res = []
        for rec in self:
            name = rec.name
            if rec.parent_id:
                name = "%s / %s" % (rec.parent_id.name, rec.name)
            res.append((rec.id, name))
        return res
