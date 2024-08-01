from odoo import api, models

from ..utils import prepare_mts_else_mto_max_qty_perc_data


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements_w_rules):
        data = prepare_mts_else_mto_max_qty_perc_data(procurements_w_rules)
        return super(
            StockRule, self.with_context(mts_else_mto_max_qty_perc_data=data)
        )._run_pull(procurements_w_rules)
