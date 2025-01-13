from odoo import models

PICKING_FINISHED_STATES = ('done', 'cancel')


class SaleOrderDeliveryProgress(models.AbstractModel):
    _name = 'sale.order.delivery.progress'
    _description = "Sale Order Delivery Progress"

    def get_progress(self, sale):
        pickings = self._get_pickings(sale)
        if not pickings:
            return 0
        total = len(pickings)
        return (self._count_finished_pickings(pickings) / total) * 100

    def _count_finished_pickings(self, pickings):
        return sum(1 for p in pickings if p.state in PICKING_FINISHED_STATES)

    def _get_pickings(self, sale):
        pickings = sale.picking_ids
        return pickings.filtered(lambda r: r.location_dest_id.usage == 'customer')
