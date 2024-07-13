from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    packaging_name = fields.Char(
        help="Will be used in product component sticker information"
    )
