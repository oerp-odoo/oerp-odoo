from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    unbuild_ids = fields.One2many(
        'mrp.unbuild',
        'mo_id',
        string="Unbuild Orders",
        auto_join=True,
    )
    unbuild_count = fields.Integer(compute='_compute_unbuild_stats')
    is_unbuilt = fields.Boolean(compute='_compute_unbuild_stats')

    @api.depends('unbuild_ids')
    def _compute_unbuild_stats(self):
        for mo in self:
            count = len(mo.unbuild_ids)
            mo.update({'unbuild_count': count, 'is_unbuilt': bool(count)})

    def action_view_unbuild_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('mrp.mrp_unbuild')
        action['domain'] = [('mo_id', '=', self.id)]
        return action
