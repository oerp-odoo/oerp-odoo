from odoo import fields, models


class MachineGroup(models.Model):
    """Model to group similar machine.instance records.

    For example production machines, staging machines etc.
    """

    _name = 'machine.group'
    _description = 'Machine Group'

    name = fields.Char(required=True, index=True)
    machine_instance_ids = fields.Many2many(
        'machine.instance',
        'machine_group_machine_instance_rel',
        'group_id',
        'instance_id',
        string="Machines",
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "The name must be unique !"),
    ]
