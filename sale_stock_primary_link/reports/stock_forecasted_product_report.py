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
        res.update({'primary_so_in': False, 'primary_so_out': False})
        if move_in:
            res['primary_so_in'] = self.sudo()._get_primary_so_data(move_in)
        if move_out:
            res['primary_so_out'] = self.sudo()._get_primary_so_data(move_out)
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

    def _get_primary_so_data(self, move):
        primary_so = self.sudo()._get_primary_so(move)
        if not primary_so:
            return False
        return {
            'name': primary_so.name,
            'id': primary_so.id,
        }
