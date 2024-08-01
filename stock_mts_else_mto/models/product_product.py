from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        res = super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
        )
        data = self.env.context.get('mts_else_mto_max_qty_perc_data')
        if data and self.env.context.get('location'):
            location_id = self.env.context['location']
            # Normalize to int
            if isinstance(location_id, list):
                location_id = location_id[0]
            # Force free_qty from context.
            for product_id in res:
                key = (location_id, product_id)
                free_qty_list = data.get(key)
                if not free_qty_list:
                    continue
                res[product_id]['free_qty'] = free_qty_list.pop()
        return res
