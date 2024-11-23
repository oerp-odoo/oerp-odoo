from odoo import api, fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    parent_root_id = fields.Many2one(
        'procurement.group',
        compute='_compute_parent_root_id',
        store=True,
        recursive=True,
    )

    @api.depends('stock_move_ids.move_dest_ids.group_id')
    def _compute_parent_root_id(self):
        for rec in self:
            rec.parent_root_id = rec._get_parent_root()

    def _get_parent_root(self):
        def get_parent(g):
            # Usually should be a single group, but either way using first found!..
            return g.stock_move_ids.move_dest_ids.group_id[:1]

        self.ensure_one()
        parent_group = self
        candidate = get_parent(parent_group)
        while candidate:
            parent_group = candidate
            candidate = get_parent(parent_group)
        return parent_group
