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
        # This is similar to mrp.production:components_availability_state,
        # but here if some date is not set, we assume its not available instead of
        # just False state!
        # Its unavailable, when at least one date that is compared, is not set.
        if any(not mo.date_start for mo in unavailable_mos) or unavailable_mos.mapped(
            'move_raw_ids'
        ).filtered(lambda r: not r.forecast_expected_date):
            return 'unavailable'
        for mo in unavailable_mos:
            raw_moves = mo.move_raw_ids
            if any(rm.forecast_expected_date > mo.date_start for rm in raw_moves):
                return 'late'
        return 'expected'
