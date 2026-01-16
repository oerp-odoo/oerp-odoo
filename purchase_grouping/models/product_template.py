from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_grouping_id = fields.Many2one(
        'purchase.grouping',
        help="If automatic purchase order is to be created for this product, it"
        + " will group by this (if vendor also matches)",
    )
