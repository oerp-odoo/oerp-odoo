from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Extend to add machine options."""

    _inherit = 'res.config.settings'

    group_machine_show_resources = fields.Boolean(
        string="Show Machine Resources",
        implied_group='machine.machine_group_show_resources',
    )
    group_machine_show_env_details = fields.Boolean(
        string="Show Machine Environment Details",
        implied_group='machine.machine_group_show_env_details',
    )
