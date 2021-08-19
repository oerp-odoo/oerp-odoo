from odoo import models


class StockPicking(models.Model):
    """Extend to add method is_closed."""

    _inherit = 'stock.picking'

    def is_closed(self):
        """Check if all pickings are done or cancelled."""
        for picking in self:
            if picking.state not in ('cancel', 'done'):
                return False
        return True
