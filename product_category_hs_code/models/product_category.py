from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    hs_code = fields.Char(
        "HS Code",
        help="Standardized code for international shipping and goods declaration.",
    )
