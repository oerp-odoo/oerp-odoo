from odoo import models

from ..utils import prepare_sale_group_name


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
            sale_lines = moves.mapped('sale_line_id')
            if sale_lines:
                res['sale_group_name'] = prepare_sale_group_name(sale_lines)
        return res
