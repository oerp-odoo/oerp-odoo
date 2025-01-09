from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_status = fields.Selection(
        [
            ('rfq', "RFQ"),
            ('confirmed', "Confirmed"),
            ('received', "Received"),
            ('done', "Done"),
        ],
        compute='_compute_purchase_status',
        store=True,
    )

    @api.depends(
        'purchase_from_primary_ids.state',
        'picking_from_primary_ids.state',
    )
    def _compute_purchase_status(self):
        SOPS = self.env['sale.order.purchase.status']
        for rec in self:
            rec.purchase_status = SOPS.get_status(rec)
