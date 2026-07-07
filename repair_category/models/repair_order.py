from odoo import fields, models


class RepairOrder(models.Model):
    """Extend to add category_id field."""

    _inherit = 'repair.order'

    category_id = fields.Many2one('repair.category')
