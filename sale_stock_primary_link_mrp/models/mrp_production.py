from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_primary_id = fields.Many2one(
        'sale.order',
        compute='_compute_sale_primary_id',
        store=True,
        string="Primary Sale Order",
        index=True,
        auto_join=True,
    )

    @api.depends('procurement_group_id.parent_root_id.sale_id')
    def _compute_sale_primary_id(self):
        for rec in self:
            sale = rec.procurement_group_id.parent_root_id.sale_id
            if sale:
                rec.sale_primary_id = sale.id
