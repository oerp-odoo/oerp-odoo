from odoo import models

from ..utils import gather_group_names_with_sale_orders, prepare_sale_group_name


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
            products = moves.mapped('product_id')
            data = gather_group_names_with_sale_orders(products, moves.group_id.sale_id)
            if data:
                res['sale_group_name'] = prepare_sale_group_name(
                    data, without_sale_name=True
                )
        return res
