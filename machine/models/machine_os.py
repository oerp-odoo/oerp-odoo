from footil.formatting import generate_names

from odoo import models, fields, api, _


class MachineOs(models.Model):
    """Model representing operating systems."""

    _name = 'machine.os'
    _description = 'Machine OS'

    name = fields.Char("Version", required=True, index=True)
    os_name_id = fields.Many2one('machine.os.name', "OS Name", required=True,)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, os_name_id)',
            _('The name must be unique per OS Name !')
        ),
    ]

    @api.depends('name', 'os_name_id.name')
    def name_get(self):
        """Override to show custom display_name."""
        return generate_names({
            'pattern': '{os_name_id.name} {name}',
            'objects': self,
        })


class MachineOsName(models.Model):
    """Model representing operating system name.

    E.g. Ubuntu, Red Hat, Windows.
    """

    _name = 'machine.os.name'
    _description = 'Machine OS Name'

    name = fields.Char(required=True, index=True)
    os_type_id = fields.Many2one('machine.os.type', "OS Type", required=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, os_type_id)',
            _('The name must be unique per OS Type !')
        ),
    ]

    @api.depends('name', 'os_type_id.name')
    def name_get(self):
        """Override to show custom display_name."""
        return generate_names({
            'pattern': '{os_type_id.name} {name}',
            'objects': self,
        })


class MachineOsType(models.Model):
    """Model representing operating system type.

    E.g. Linux, Unix, Windows.
    """

    _name = 'machine.os.type'
    _description = 'Machine OS Type'

    name = fields.Char(required=True,)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The name must be unique !')),
    ]
