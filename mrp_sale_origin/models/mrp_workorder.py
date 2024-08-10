from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    sale_origin = fields.Char(
        related='production_id.sale_origin',
        store=True,
    )
