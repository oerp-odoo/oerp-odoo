from odoo import fields, models

from .. import const


class PackageLamination(models.Model):

    _name = 'package.lamination'
    _description = "Package Lamination"

    name = fields.Char(required=True)
    unit_cost = fields.Float(required=True, digits=const.DecimalPrecision.COST)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
