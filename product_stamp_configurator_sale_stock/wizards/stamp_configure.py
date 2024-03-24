from odoo import models


class StampConfigure(models.TransientModel):
    """Extend to integrate with stock."""

    _inherit = 'stamp.configure'

    def _prepare_common_product_die_vals(self):
        res = super()._prepare_common_product_die_vals()
        company = self.company_id
        routes = company.stock_route_stamp_default_ids
        # If no routes are set, then it means we force to not set any
        # routes (even default ones that would normally come).
        res['route_ids'] = [(6, 0, routes.ids)]
        return res
