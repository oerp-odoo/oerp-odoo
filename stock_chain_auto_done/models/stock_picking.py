from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        SCAD = self.env['stock.chain.auto.done']
        for picking in self:
            if picking.state != 'done':
                continue
            SCAD.handle_chain_done(picking)
        return res
