from odoo import models


class StockMove(models.Model):
    """Extend to be able to prepare partial move lines per move."""

    _inherit = 'stock.move'

    def _prepare_partial_move_lines(self):
        def append_vals(qty_done):
            data.append(
                (
                    0,
                    0,
                    {
                        'product_id': product.id,
                        'product_uom_id': self.product_uom.id,
                        'move_id': self.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'qty_done': qty_done,
                    },
                )
            )

        self.ensure_one()
        product = self.product_id
        data = []
        if product.tracking != 'serial':
            append_vals(self.product_uom_qty)
            return data
        # We can naively convert float to int, because serial numbers
        # are expected to be whole numbers only anyway!
        for __ in range(int(self.product_uom_qty)):
            # 1 per serial number
            append_vals(1)
        return data
