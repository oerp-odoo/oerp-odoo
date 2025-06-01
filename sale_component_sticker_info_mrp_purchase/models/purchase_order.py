from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()
        PCSIS = self.env['purchase.component.sticker.info.send']
        for po in self:
            PCSIS.send_message(po)
        return res
