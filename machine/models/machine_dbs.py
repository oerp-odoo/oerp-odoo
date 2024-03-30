from footil.formatting import generate_names

from odoo import _, api, fields, models


class MachineDbs(models.Model):
    """Model representing specific database system version."""

    _name = 'machine.dbs'
    _description = 'Machine Database System'

    name = fields.Char("Version", required=True, index=True)
    dbs_name_id = fields.Many2one(
        'machine.dbs.name',
        "Database Name",
        required=True,
    )

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name, dbs_name_id)',
            "The name must be unique per Database Name !",
        ),
    ]

    @api.depends('name', 'dbs_name_id.name')
    def name_get(self):
        """Override to show custom display_name."""
        return generate_names(
            {
                'pattern': '{dbs_name_id.name} {name}',
                'objects': self,
            }
        )


class MachineDbsName(models.Model):
    """Model representing database name.

    E.g. PostgreSQL, MySQL.
    """

    _name = 'machine.dbs.name'
    _description = 'Machine Database System Name'

    name = fields.Char(required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('The name must be unique !')),
    ]
