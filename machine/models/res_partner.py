from odoo import models, fields, api


class ResPartner(models.Model):
    """Extend to relate it with `machine.instance` records."""

    _inherit = 'res.partner'

    machine_instance_ids = fields.One2many(
        'machine.instance',
        'partner_id',
        "Machine Instances",
        groups="machine.machine_group_user")
    machine_instance_count = fields.Integer(
        "Machine Instance Count",
        compute='_compute_machine_instance_count',
        groups="machine.machine_group_user")

    @api.one
    @api.depends('machine_instance_ids')
    def _compute_machine_instance_count(self):
        self.machine_instance_count = len(self.machine_instance_ids)
