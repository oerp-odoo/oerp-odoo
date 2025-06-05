from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_primary_tag_ids = fields.Many2many(
        related='sale_primary_id.tag_ids', string="Primary Sale Order's Tags"
    )
