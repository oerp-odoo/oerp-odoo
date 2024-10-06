from odoo import models

from .. import utils


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        res = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        moves = values.get('move_dest_ids')
        if moves:
            sale_lines = utils.get_sale_lines_from_stock_moves(moves)
            if sale_lines:
                res['sale_group_name'] = utils.prepare_sale_group_name(sale_lines)
        return res
