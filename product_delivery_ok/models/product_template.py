from odoo import models, fields


class ProductTemplate(models.Model):
    """Extend to add delivery_ok field."""

    _inherit = 'product.template'

    delivery_ok = fields.Boolean('Used for Delivery')
