from odoo import fields, models


class StockPickingType(models.Model):
    """Extend to add field partial_prefill_move_lines."""

    _inherit = 'stock.picking.type'

    partial_prefill_move_lines = fields.Boolean(
        "Partially Pre-fill Detailed Operations",
        help="When picking is confirmed, detailed operations will be"
        + " partially pre filled",
    )
