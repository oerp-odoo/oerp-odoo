from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_code = fields.Char(copy=False)

    _pricelist_code_uniq = models.Constraint(
        'unique (pricelist_code)',
        'The Pricelist Code must be unique!',
    )
