from odoo import models

MO_FINISHED_STATES = ('done', 'cancel')


class SaleOrderComponentAvailability(models.AbstractModel):
    _name = 'sale.order.component.availability'
    _description = "Sale Order Component Availability"

    def get_availability_info(self, sale):
        mos = sale.production_from_primary_ids
        if not mos:
            return (False, 0)
        total = len(mos)
        available_mos = self._filter_available_mos(mos)
        count = (len(available_mos) / total) * 100
        if count == 100:
            return ('available', 100)
        unavailable_mos = mos - available_mos
        state = self._get_unavailability_state(sale, unavailable_mos)
        return (state, count)

    def _filter_available_mos(self, mos):
        return mos.filtered(
            lambda r: r.state in MO_FINISHED_STATES
            or r.components_availability_state == 'available'
        )

    def _get_unavailability_state(self, sale, unavailable_mos):
        dt_commitment = sale.commitment_date
        if not dt_commitment:
            return 'late'
        for mo in unavailable_mos:
            if not mo.date_start or mo.date_start > dt_commitment:
                return 'late'
        return 'unavailable'
