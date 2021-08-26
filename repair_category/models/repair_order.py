from odoo import models, fields


class RepairOrder(models.Model):
    """Extend to category_id field."""

    _inherit = 'repair.order'

    category_id = fields.Many2one('repair.category')
    product_uom_category_id = fields.Many2one(string="UoM Category")
