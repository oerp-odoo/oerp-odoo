from odoo import models

RFQ_STATES = ('draft', 'sent', 'to approve')
XMLID_LOC_INPUT = 'stock.stock_location_company'


class SaleOrderPurchaseStatus(models.AbstractModel):
    _name = 'sale.order.purchase.status'
    _description = "Sale Order Purchase Status"

    def get_status(self, sale):
        purchases = self._get_purchases_for_status(sale)
        if not purchases:
            return False
        if self._is_purchase_status_rfq(purchases):
            return 'rfq'
        in_pickings, input_to_stock_pickings = self._get_in_pickings_for_status(sale)
        if self._is_purchase_status_confirmed(in_pickings):
            return 'confirmed'
        if self._is_purchase_status_received(in_pickings, input_to_stock_pickings):
            return 'received'
        return 'done'

    def _get_purchases_for_status(self, sale):
        return sale.purchase_from_primary_ids.filtered(lambda r: r.state != 'cancel')

    def _get_in_pickings_for_status(self, sale):
        """Return receipt pickings and internal pickings from input to stock."""
        pickings = sale.picking_from_primary_ids.filtered(lambda r: r.state != 'cancel')
        # With single step, this will be to stock pickings, with two
        # steps, it will be to input!
        in_pickings = pickings.filtered(lambda r: r.picking_type_id.code == 'incoming')
        input_to_stock_pickings = pickings.filtered(
            lambda r: r.picking_type_id.code == 'internal'
            # TODO: should we check only one specific Input location?..
            and r.location_id == self.env.ref(XMLID_LOC_INPUT)
            and r.location_dest_id.usage == 'internal'
        )
        return (in_pickings, input_to_stock_pickings)

    def _is_purchase_status_rfq(self, purchases):
        return any(p.state in RFQ_STATES for p in purchases)

    def _is_purchase_status_confirmed(self, in_pickings):
        return any(p.state != 'done' for p in in_pickings)

    def _is_purchase_status_received(self, in_pickings, input_to_stock_pickings):
        # input_to_stock_pickings shows that it is a two step process, and
        # received status can be used with two steps only!
        return (
            input_to_stock_pickings
            and all(p.state == 'done' for p in in_pickings)
            and any(p.state != 'done' for p in input_to_stock_pickings)
        )
