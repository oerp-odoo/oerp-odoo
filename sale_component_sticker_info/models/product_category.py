from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_group = fields.Char(
        string="Group",
        help="Group to group products on sale order lines",
        company_dependent=True,
    )
