from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_paid(self):
        """Extend to auto done related POs if enabled."""
        super().action_invoice_paid()
        for invoice in self:
            # User might not have access to purchase.
            purchases = invoice.sudo().invoice_line_ids.mapped(
                'purchase_line_id.order_id'
            )
            for purchase in purchases:
                purchase.check_and_set_purchase_done()
