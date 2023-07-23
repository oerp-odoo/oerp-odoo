from odoo import api, models


class StockProductionLot(models.Model):
    """Extend to modify serial numbers creation."""

    _inherit = 'stock.production.lot'

    @api.model_create_multi
    def create(self, vals_list):
        """Extend to use custom vals from context."""
        data = self._context.get('serial_numbers_file_data')
        if data:
            for vals in vals_list:
                name = vals.get('name')
                if name:
                    vals.update(data[name])
        return super().create(vals_list)
