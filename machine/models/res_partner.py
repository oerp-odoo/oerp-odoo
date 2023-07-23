from odoo import api, fields, models


class ResPartner(models.Model):
    """Extend to relate it with `machine.instance` records."""

    _inherit = 'res.partner'

    machine_instance_ids = fields.One2many(
        'machine.instance',
        'partner_id',
        "Machines",
        groups="machine.machine_group_user",
    )
    machine_instance_count = fields.Integer(
        "Machines Count",
        compute='_compute_machine_instance_count',
        groups="machine.machine_group_user",
    )

    @api.depends('machine_instance_ids')
    def _compute_machine_instance_count(self):
        for rec in self:
            rec.machine_instance_count = len(rec.machine_instance_ids)
