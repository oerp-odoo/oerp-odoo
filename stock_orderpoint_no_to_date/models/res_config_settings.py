from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    orderpoint_no_to_date = fields.Boolean(
        related='company_id.orderpoint_no_to_date',
        readonly=False,
    )
