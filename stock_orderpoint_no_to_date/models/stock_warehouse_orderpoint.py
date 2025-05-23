from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def _get_product_context(self, visibility_days=0):
        res = super()._get_product_context(visibility_days=visibility_days)
        if self.company_id.orderpoint_no_to_date:
            res.pop('to_date')
        return res
