import ast

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _set_pending(self, state_message=None):
        for tx in self:
            ctx = {}
            mail_tmpl = tx.acquirer_id.mail_template_sale_confirm_id
            sale_orders = tx.sale_order_ids.filtered(
                lambda r: r.state in ('draft', 'sent')
            )
            if mail_tmpl and sale_orders:
                ctx['force_mail_template_sale_confirm_id'] = mail_tmpl.id
                extra_ctx = tx.acquirer_id.mail_template_sale_confirm_ctx
                if extra_ctx:
                    ctx.update(**ast.literal_eval(extra_ctx))
            super(PaymentTransaction, tx.with_context(**ctx))._set_pending(
                state_message=state_message
            )
