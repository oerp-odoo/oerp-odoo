from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    die_default_id = fields.Many2one(
        related='company_id.die_default_id', readonly=False
    )
    category_default_counter_die_id = fields.Many2one(
        related='company_id.category_default_counter_die_id',
        readonly=False,
    )
    category_default_mold_id = fields.Many2one(
        related='company_id.category_default_mold_id',
        readonly=False,
    )
    quantity_mold_default = fields.Integer(
        related='company_id.quantity_mold_default',
        readonly=False,
    )
