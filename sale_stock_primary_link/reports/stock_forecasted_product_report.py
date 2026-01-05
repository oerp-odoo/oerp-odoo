from odoo import models


class StockForecastedProductProduct(models.AbstractModel):
    _inherit = 'stock.forecasted_product_product'

    def _prepare_report_line(
        self,
        quantity,
        move_out=None,
        move_in=None,
        replenishment_filled=True,
        product=False,
        reserved_move=False,
        in_transit=False,
        read=True,
    ):
        res = super()._prepare_report_line(
            quantity,
            move_out=move_out,
            move_in=move_in,
            replenishment_filled=replenishment_filled,
            product=product,
            reserved_move=reserved_move,
            in_transit=in_transit,
            read=read,
        )
        res['primary_so'] = False
        move = move_in or move_out
        if move:
            primary_so = self.sudo()._get_primary_so(move)
            if primary_so:
                res['primary_so'] = {
                    'name': primary_so.name,
                    'id': primary_so.id,
                }
        return res

    def _get_primary_so(self, move):
        source_rec = move._get_source_document()
        if source_rec._name == 'sale.order':
            return source_rec
        if hasattr(source_rec, 'sale_primary_id'):
            return source_rec['sale_primary_id']
        if source_rec._name == 'stock.move':
            return source_rec.picking_id.sale_primary_id
        return self.env['sale.order']
