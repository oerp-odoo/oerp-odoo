from odoo import models, fields


class StockMove(models.Model):
    """Extend to add selling_price field."""

    _inherit = 'stock.move'

    # Renaming original field label to make sense what it means.
    price_unit = fields.Float('Unit Cost')
    price_selling_unit = fields.Float(
        string="Unit Price", default=0.0, digits='Product Price'
    )
    use_selling_price = fields.Boolean(related='picking_id.use_selling_price')
