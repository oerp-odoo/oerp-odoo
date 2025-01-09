from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_from_primary_ids = fields.One2many('purchase.order', 'sale_primary_id')
