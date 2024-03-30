from odoo import api, fields, models


class StockPicking(models.Model):
    """Extent to add use_selling_price, amount_total_selling_price."""

    _inherit = 'stock.picking'

    # Label different to indicate main reason this field is used for.
    use_selling_price = fields.Boolean("Sample For Marketing")
    amount_total_selling_price = fields.Float(
        compute='_compute_amount_total_selling_price',
        string="Total Selling Price",
        store=True,
        digits='Product Price',
    )

    @api.depends('move_lines.price_selling_unit')
    def _compute_amount_total_selling_price(self):
        for picking in self:
            picking.amount_total_selling_price = sum(
                move.price_selling_unit * move.product_uom_qty
                for move in picking.move_lines
            )
