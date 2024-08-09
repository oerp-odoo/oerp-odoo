from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_origin = fields.Char(
        string="Sale Source",
        compute='_compute_sale_origin',
        store=True,
        help="Reference of the document that generated related sale order",
    )

    @api.depends(
        'procurement_group_id.mrp_production_ids.move_dest_ids.'
        + 'group_id.sale_id.origin'
    )
    def _compute_sale_origin(self):
        for rec in self:
            sales = rec.procurement_group_id.mapped(
                'mrp_production_ids.move_dest_ids.group_id.sale_id'
            )
            origins = [so.origin for so in sales if so.origin]
            rec.sale_origin = ','.join(origins) or False
