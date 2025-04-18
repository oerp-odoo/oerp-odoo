from odoo import api, fields, models

from .. import const


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Note this will show only directly related from MO, but value itself
    # is coming originally from sale order!
    sale_group_name = fields.Char(
        compute='_compute_sale_group_name',
        help="Showing from related Manufacturing Orders",
    )

    @property
    def _sale_group_name(self):
        self.ensure_one()
        group_names = self.group_id.mrp_production_ids.mapped('sale_group_name')
        # List could consist of False values.
        group_names = [g for g in group_names if g]
        if not group_names:
            return False
        return const.STICKER_INFO_SEP.join(group_names)

    @api.depends('group_id.mrp_production_ids.sale_group_name')
    def _compute_sale_group_name(self):
        for rec in self:
            rec.sale_group_name = rec._sale_group_name
