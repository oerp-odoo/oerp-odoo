from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    location_src_default_repair_id = fields.Many2one(
        related='company_id.location_src_default_repair_id',
        readonly=False,
    )
    location_dest_add_operation_repair_id = fields.Many2one(
        related='company_id.location_dest_add_operation_repair_id',
        readonly=False,
    )
