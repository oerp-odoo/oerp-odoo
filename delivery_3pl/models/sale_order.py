from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_warehouse_id(self):
        super()._compute_warehouse_id()
        for sale in self:
            service = self.env['tpl.service'].get_3pl_service(
                sale, raise_not_found=False
            )
            if service.warehouse_id:
                sale.warehouse_id = service.warehouse_id
