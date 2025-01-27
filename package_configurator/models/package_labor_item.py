from odoo import api, fields, models

from .. import const


class PackageLaborItem(models.Model):
    _name = 'package.labor.item'
    _description = "Package Labor Item"

    labor_id = fields.Many2one('package.labor', required=True)
    labor_type_id = fields.Many2one('package.labor.type', required=True)
    # Used in generic type case.
    custom_name = fields.Char()
    units_per_hour = fields.Integer("Units per Hour")
    setup_minutes = fields.Integer()
    # TODO: implement to_fit support!
    to_fit = fields.Boolean(
        help="Whether try to use fit quantity and fit as many components as possible"
        + " per process unit. If checked, fit quantity will be used to divide demanded"
        + " quantity, meaning it could reuse more components on single raw sheet."
    )
    is_generic = fields.Boolean(compute='_compute_is_generic')
    # TODO: add dynamic HTML description to show some useful information about each
    # labor type and chosen options.

    @api.depends('labor_type_id')
    def _compute_is_generic(self):
        for rec in self:
            rec.is_generic = rec.labor_type_id.code == const.LaborType.GENERIC
