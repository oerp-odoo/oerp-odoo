from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    production_origin = fields.Char(
        string="Manufacturing Source",
        related='production_id.origin',
        store=True,
    )
