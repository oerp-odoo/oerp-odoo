from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    intrastat_stamp_default_code_id = fields.Many2one(
        related='company_id.intrastat_stamp_default_code_id',
        readonly=False,
    )
