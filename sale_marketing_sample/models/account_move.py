from odoo import fields, models


class AccountMove(models.Model):
    """Extend to add is_marketing field."""

    _inherit = 'account.move'

    is_marketing = fields.Boolean("Sample For Marketing", readonly=True)

    def _auto_pay_move(self):
        def get_journal_id(company_id):
            return (
                self.env['account.journal']
                .search(
                    [('type', '=', 'bank'), ('company_id', '=', company_id)],
                    limit=1,
                )
                .id
            )

        self.ensure_one()
        # Ignore auto pay if some other workflow already paid this
        # invoice.
        if self.payment_state in ('in_payment', 'paid'):
            return False
        AccountPaymentRegister = self.env['account.payment.register']
        payment_register = AccountPaymentRegister.with_context(
            active_ids=[self.id], active_model='account.move'
        ).create({'journal_id': get_journal_id(self.company_id.id)})
        payment_register.action_create_payments()
        return True

    def action_post(self):
        """Extend to auto pay invoices that have is_marketing=True."""
        res = super().action_post()
        for move in self.filtered('is_marketing'):
            move._auto_pay_move()
        return res
