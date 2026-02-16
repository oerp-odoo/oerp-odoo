from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_code = fields.Char(copy=False)

    _sql_constraints = [
        (
            'pricelist_code_uniq',
            'unique (pricelist_code)',
            'The Pricelist Code must be unique !',
        )
    ]
