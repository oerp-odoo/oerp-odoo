from odoo import models


class StockMoveLine(models.Model):
    """Extend to add selling price in aggregated lines."""

    _inherit = 'stock.move.line'

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(
            **kwargs
        )
        moves = self.mapped('move_id')
        for aggregated_move_line in aggregated_move_lines:
            use_selling_price = False
            product = aggregated_move_lines[aggregated_move_line]['product']
            # Assuming unique products match number of moves.
            move = moves.filtered(lambda r: r.product_id == product)
            if move:
                use_selling_price = move.picking_id.use_selling_price
                price_selling_unit = move[0].price_selling_unit
                aggregated_move_lines[aggregated_move_line][
                    'price_selling_unit'
                ] = price_selling_unit
            aggregated_move_lines[aggregated_move_line][
                'use_selling_price'
            ] = use_selling_price
        return aggregated_move_lines
