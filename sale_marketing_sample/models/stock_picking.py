from odoo import models, fields


class StockPicking(models.Model):
    """Extend to make use_selling_price readonly."""

    _inherit = 'stock.picking'

    use_selling_price = fields.Boolean(readonly=True)
