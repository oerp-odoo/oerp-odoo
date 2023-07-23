from odoo import fields, models


class RepairLine(models.Model):
    """Extend to change product_uom_category_id label."""

    _inherit = 'repair.line'

    product_uom_category_id = fields.Many2one(string="UoM Category")
