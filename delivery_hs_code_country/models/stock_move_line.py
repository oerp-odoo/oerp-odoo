from odoo import models


def pridecate_move_product(product):
    return lambda r: r.product_id == product


class StockMoveLine(models.Model):
    """Extend to use hs_code by country aggregated lines."""

    _inherit = 'stock.move.line'

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        moves = self.mapped('move_id')
        for aggregated_move_line in aggregated_move_lines:
            product = aggregated_move_lines[aggregated_move_line]['product']
            # Assuming unique products match number of moves.
            move = moves.filtered(pridecate_move_product(product))
            if move:
                country_code = move.picking_id.partner_id.country_id.code
                hs_code = product.retrieve_hs_code(country_code=country_code)
                aggregated_move_lines[aggregated_move_line]['hs_code'] = hs_code
        return aggregated_move_lines
