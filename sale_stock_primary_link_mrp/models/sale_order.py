from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_from_primary_ids = fields.One2many('mrp.production', 'sale_primary_id')
