from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _prepare_qty_done(self):
        self.ensure_one()
        return {
            'code': self.product_id.default_code,
            'quantity': self.qty_done,
        }
