from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        super()._action_done()
        for picking in self:
            # User might not have access to purchase.
            purchase = picking.sudo().purchase_id
            if purchase:
                purchase.sudo().check_and_set_purchase_done()
