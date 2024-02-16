from odoo import models, api


class RepairLine(models.Model):
    _inherit = 'repair.line'

    @api.onchange('type')
    def onchange_operation_type(self):
        super().onchange_operation_type()
        if (
            self.type == 'add'
            and self.company_id.location_dest_add_operation_repair_id
        ):
            self.location_dest_id = (
                self.company_id.location_dest_add_operation_repair_id
            )
