from odoo import models, api
from odoo.osv import expression


class SaleOrder(models.Model):
    """Extend to add functionality that can auto lock needed orders."""

    _inherit = 'sale.order'

    def _prepare_orders_to_lock_domain(self, args=None):
        domain = [('state', '=', 'sale'), ('invoice_status', '=', 'invoiced')]
        if args:
            domain = expression.AND([domain, args])
        return domain

    def _is_order_fulfilled(self):
        self.ensure_one()
        for line in self.order_line:
            qty_ordered = line.product_uom_qty
            if (
                qty_ordered != line.qty_invoiced or
                (
                    line.product_id.type != 'service' and
                    qty_ordered != line.qty_delivered
                )
            ):
                return False
        return True

    @api.model
    def _find_orders_to_lock(self, args=None):
        domain = self._prepare_orders_to_lock_domain(args=args)
        sales = self.search(domain)
        sales_to_lock = self.env[self._name]
        for sale in sales:
            if (
                sale._is_order_fulfilled() and
                sale.picking_ids.is_closed() and
                sale.invoice_ids.is_closed()
            ):
                sales_to_lock |= sale
        return sales_to_lock

    @api.model
    def _find_and_lock_orders(self, args=None):
        sales_to_lock = self._find_orders_to_lock(args=args)
        if sales_to_lock:
            sales_to_lock.action_done()
        return sales_to_lock
