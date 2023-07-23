from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    category_default_counter_die_id = fields.Many2one(
        related='company_id.category_default_counter_die_id',
        readonly=False,
    )
    category_default_mold_id = fields.Many2one(
        related='company_id.category_default_mold_id',
        readonly=False,
    )
