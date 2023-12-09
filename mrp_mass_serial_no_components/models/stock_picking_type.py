from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    mass_serial_ignore_components = fields.Boolean(
        "MRP Mass Serial Numbers with Missing Components",
        help="Even if components are missing, it will allow to mass produce"
        + " serials.",
    )
