from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        to_auto_plan = records.filtered(lambda r: r.bom_id.auto_plan)
        if to_auto_plan:
            to_auto_plan.button_plan()
        return records
