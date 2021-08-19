from odoo import models


class AccountInvoice(models.Model):
    """Extend to add method is_closed."""

    _inherit = 'account.invoice'

    def is_closed(self):
        """Check if all invoices are paid or cancelled."""
        for inv in self:
            if inv.state not in ('cancel', 'paid'):
                return False
        return True
