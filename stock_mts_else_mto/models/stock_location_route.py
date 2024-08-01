from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    mts_else_mto_condition = fields.Selection(
        [('orderpoint_max_qty_perc', "Reordering Rule Max Quantity Percentage")],
        string="MTS/MTO Condition",
        help="* Reordering Rule Max Quantity Percentage: "
        + "MTO will trigger if demand is higher than specified reordering rule MAX "
        + "quantity percentage"
        + "\nSelected condition only works for products with "
        + "reordering rule(-s) and this route",
    )
    orderpoint_max_qty_perc = fields.Float("Reordering Rule Max Quantity Percentage")
