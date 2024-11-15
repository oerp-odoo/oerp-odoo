from odoo import fields, models

from .. import const


class PackagePrintPricelistRule(models.Model):
    _name = 'package.print.pricelist.rule'
    _description = "Package Print Pricelist Rule"
    _order = 'color_id, min_qty desc, id'

    print_pricelist_id = fields.Many2one('package.print.pricelist', required=True)
    color_id = fields.Many2one('package.print.color', required=True)
    min_qty = fields.Integer(
        "Minimum Sheet Quantity",
        help="Minimum raw sheet quantity for given unit cost",
        required=True,
    )
    unit_cost = fields.Float(required=True, digits=const.DecimalPrecision.COST)

    def is_match(self, color, quantity):
        self.ensure_one()
        return self.color_id == color and quantity >= self.min_qty
