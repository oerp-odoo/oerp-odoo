from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    package_default_lid_extra = fields.Float(
        related='company_id.package_default_lid_extra', readonly=False
    )
    package_default_outside_wrapping_extra = fields.Float(
        related='company_id.package_default_outside_wrapping_extra', readonly=False
    )
