from odoo import models, fields


class ProductTemplate(models.Model):
    """Extend to add description_rich_delivery field."""

    _inherit = 'product.template'

    description_rich_delivery = fields.Html(
        'Delivery Rich Description', translate=True, sanitize=False
    )
