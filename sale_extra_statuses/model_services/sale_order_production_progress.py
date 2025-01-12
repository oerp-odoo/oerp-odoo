from odoo import models

MO_FINISHED_STATES = ('done', 'cancel')


class SaleOrderProductionProgress(models.AbstractModel):
    _name = 'sale.order.production.progress'
    _description = "Sale Order Production Progress"

    def get_progress(self, sale):
        mos = sale.production_from_primary_ids
        if not mos:
            return 0
        total = len(mos)
        return (self._count_finished_mos(mos) / total) * 100

    def _count_finished_mos(self, mos):
        return sum(1 for mo in mos if mo.state in MO_FINISHED_STATES)
