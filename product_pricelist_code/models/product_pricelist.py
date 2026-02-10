from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    code = fields.Char(copy=False)

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
