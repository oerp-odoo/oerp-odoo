from odoo import models

from .res_config_settings import CFG_PARAM_PO_AUTO_DONE


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def check_and_set_purchase_done(self):
        self.ensure_one()
        if (
            not self.env['ir.config_parameter'].sudo().get_param(CFG_PARAM_PO_AUTO_DONE)
            or self.state == 'done'
        ):
            return False
        if self.is_purchase_done():
            self.button_done()
            return True
        return False

    def is_purchase_done(self):
        self.ensure_one()
        if any(not line.is_line_done() for line in self.order_line):
            return False
        pickings = self.picking_ids.filtered(lambda r: r.state != 'cancel')
        # All pickings must be done.
        if any(p.state != 'done' for p in pickings):
            return False
        invoices = self.invoice_ids.filtered(lambda r: r.state != 'cancel')
        return all(
            inv.state == 'posted' and inv.payment_state in ('paid', 'in_payment')
            for inv in invoices
        )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def is_line_done(self):
        self.ensure_one()
        return self.display_type or (
            self.qty_received >= self.product_qty
            and self.qty_invoiced >= self.product_qty
        )
