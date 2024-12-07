from odoo import api, fields, models

from .. import const
from ..utils.misc import get_selection_label


class PackageStamp(models.Model):
    _name = 'package.stamp'
    _inherit = 'package.area.range.mixin'
    _description = "Package Stamp"
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name')
    stamp_type = fields.Selection(
        [('emboss', 'Embossed'), ('deboss', 'Debossed')],
        default='emboss',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    cost = fields.Float("Tool Cost", digits=const.DecimalPrecision.COST)

    @api.depends('stamp_type', 'area_range_from_id', 'area_range_to_id')
    def _compute_name(self):
        for rec in self:
            range_name = rec.area_range_name
            label = get_selection_label(rec, 'stamp_type')
            rec.name = f'{range_name} ({label})'
