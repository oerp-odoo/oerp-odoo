from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_from_primary_ids = fields.One2many('stock.picking', 'sale_primary_id')
