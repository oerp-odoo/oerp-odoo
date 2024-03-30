from odoo import api, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super()._onchange_company_id()
        if self.company_id.location_src_default_repair_id:
            self.location_id = self.company_id.location_src_default_repair_id
