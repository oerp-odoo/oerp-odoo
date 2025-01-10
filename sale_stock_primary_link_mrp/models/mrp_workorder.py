from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    sale_primary_id = fields.Many2one(
        related='production_id.sale_primary_id', store=True
    )
