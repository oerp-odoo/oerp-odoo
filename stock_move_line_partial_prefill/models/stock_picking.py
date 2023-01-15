from odoo import models


class StockPicking(models.Model):
    """Extend to add move lines partial prefill feature on confirm."""

    _inherit = 'stock.picking'

    def action_confirm(self):
        """Extend to partially prefill move lines if enabled."""
        res = super().action_confirm()
        for picking in self:
            picking_type = picking.picking_type_id
            move_lines = picking.move_line_ids
            if (
                picking_type.partial_prefill_move_lines
                and picking_type.show_operations
                and not move_lines
                and picking_type.reservation_method == 'manual'
            ):
                picking._prefill_move_lines_partially()
        return res

    def _prefill_move_lines_partially(self):
        self.ensure_one()
        datas = []
        # NOTE. move_lines is actually moves, not lines.. Crappy odoo
        # naming..
        for stock_move in self.move_lines:
            datas.extend(stock_move._prepare_partial_move_lines())
        if datas:
            self.move_line_ids = datas
