from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_grouping = fields.Selection(
        related='company_id.purchase_grouping',
        readonly=False,
    )
