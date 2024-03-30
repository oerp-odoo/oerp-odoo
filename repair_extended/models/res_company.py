from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    location_src_default_repair_id = fields.Many2one(
        'stock.location', string="Default Repair Source Location"
    )
    location_dest_add_operation_repair_id = fields.Many2one(
        'stock.location',
        string="Default Repair Destination Add Operation Location",
    )
