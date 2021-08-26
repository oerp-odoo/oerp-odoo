from odoo import models, fields


class RepairFee(models.Model):
    """Extend to change product_uom_category_id label."""

    _inherit = 'repair.fee'

    product_uom_category_id = fields.Many2one(string="UoM Category")
