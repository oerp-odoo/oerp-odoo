from odoo import models, fields

_M = 'mass_mailing_contact_fields'


class ResConfigSettings(models.TransientModel):
    """Extend to add options that show/hide fields."""

    _inherit = 'res.config.settings'

    group_mailing_show_state = fields.Boolean(
        string="Show Mailing Contact State",
        implied_group=f'{_M}.mailing_group_show_state',
    )
    group_mailing_show_city = fields.Boolean(
        string="Show Mailing Contact City",
        implied_group=f'{_M}.mailing_group_show_city',
    )
    group_mailing_show_postcode = fields.Boolean(
        string="Show Mailing Contact ZIP",
        implied_group=f'{_M}.mailing_group_show_postcode',
    )
    group_mailing_show_phone = fields.Boolean(
        string="Show Mailing Contact Phone",
        implied_group=f'{_M}.mailing_group_show_phone',
    )
