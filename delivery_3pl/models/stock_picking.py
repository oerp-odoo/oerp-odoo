from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # TODO would make more sense on some more generic module.
    def _send_confirmation_email(self):
        pickings = self
        if self.env.context.get('stock_move_email_on_done'):
            # Send confirmation email only if picking is truly done!
            pickings = self.filtered(lambda r: r.state == 'done')
        super(StockPicking, pickings)._send_confirmation_email()
