from odoo import fields, models


class PackageConfiguratorCirculation(models.AbstractModel):
    """Base model to handle circulation variants (quantity) of a package.

    For example, there could be circulation of 100, 1000, 10000 quantities of the same
    product.
    """

    _name = 'package.configurator.circulation'
    _description = "Package Configurator Circulation"

    configurator_id = fields.Many2one('package.configurator', required=True)
    quantity = fields.Integer(required=True)
