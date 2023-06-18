from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_3pl_warehouse(self, vals):
        """Extend to find warehouse for specific 3PL service."""
        # TODO: need mechanism for multiple 3PL services to know which
        # one's default to use.
        return self.env['stock.warehouse']

    def get_3pl_service(self, name, raise_not_found=True):
        """Extend to implement way to find specific 3PL service."""
        self.ensure_one()
        return self.env['tpl.service']

    @api.model
    def create(self, vals):
        if 'warehouse_id' not in vals:
            warehouse = self.get_3pl_warehouse(vals)
            if warehouse:
                vals['warehouse_id'] = warehouse.id
        return super().create(vals)
