from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_primary_id = fields.Many2one(
        'sale.order',
        compute='_compute_sale_primary_id',
        store=True,
        string="Primary Sale Order",
    )

    @api.depends('group_id.parent_root_id.sale_id')
    def _compute_sale_primary_id(self):
        for rec in self:
            sale = rec.group_id.parent_root_id.sale_id
            if sale:
                rec.sale_primary_id = sale.id
