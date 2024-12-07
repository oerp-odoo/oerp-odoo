from odoo import api, fields, models

from .. import const


class PackageFoil(models.Model):
    _name = 'package.foil'
    _inherit = 'package.area.range.mixin'
    _description = "Package Foil"
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name')
    engraved = fields.Boolean()
    form_cost = fields.Float(digits=const.DecimalPrecision.COST)
    unit_cost = fields.Float(digits=const.DecimalPrecision.COST)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    @api.depends('engraved', 'area_range_from_id', 'area_range_to_id')
    def _compute_name(self):
        for rec in self:
            name = rec.area_range_name
            if rec.engraved:
                name = f'{name} (Engraved)'
            rec.name = name
