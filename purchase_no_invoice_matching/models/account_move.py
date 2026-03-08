from odoo import models

from ..const import CFG_PARAM_NO_INVOICE_MATCHING


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _match_purchase_orders(
        self, po_references, partner_id, amount_total, from_ocr, timeout
    ):
        if (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_NO_INVOICE_MATCHING)
        ):
            return ('no_match', self.env['purchase.order.line'], None)
        return super()._match_purchase_orders(
            po_references, partner_id, amount_total, from_ocr, timeout
        )
