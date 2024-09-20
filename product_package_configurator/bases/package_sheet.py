from odoo import fields, models

from .. import const


class PackageSheet(models.AbstractModel):

    _name = 'package.sheet'
    _description = "Package Sheet"

    unit_cost = fields.Float(required=True, digits=const.DecimalPrecision.COST)
    sheet_length = fields.Float(
        "Length, mm", required=True, digits=const.DecimalPrecision.SIZE
    )
    sheet_width = fields.Float(
        "Width, mm", required=True, digits=const.DecimalPrecision.SIZE
    )
    min_qty = fields.Integer(
        string="MOQ",
        help="Minimum order quantity of sheets to be used regardless of how many are"
        + " needed.",
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
