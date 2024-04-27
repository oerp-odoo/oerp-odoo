from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_global_partner = fields.Boolean(
        related='website_id.is_global_partner', readonly=False
    )
