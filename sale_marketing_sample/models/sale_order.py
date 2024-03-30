from odoo import fields, models


class SaleOrder(models.Model):
    """Extend to add is_marketing field and its workflow."""

    _inherit = 'sale.order'

    is_marketing = fields.Boolean("Sample For Marketing")

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['is_marketing'] = self.is_marketing
        return res

    def action_confirm(self):
        """Extend to propagate is_marketing val for related pickings."""
        res = super().action_confirm()
        sale_marketing = self.filtered("is_marketing")
        pickings = sale_marketing.mapped('picking_ids')
        if pickings:
            pickings.write({'use_selling_price': True})
        return res
