from odoo import models


class StampConfigure(models.TransientModel):
    """Extend to integrate with opportunities."""

    _inherit = 'stamp.configure'

    def find_rel_document_products(self):
        """Extend to include products from opp related other sales."""
        products = super().find_rel_document_products()
        other_sales = self.sale_id.opportunity_id.order_ids - self.sale_id
        return products | other_sales.mapped('order_line.product_id')
