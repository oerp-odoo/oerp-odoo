from odoo import models, fields


class ProductTemplate(models.Model):
    """Extend to add description_rich field."""

    _inherit = 'product.template'

    description_rich = fields.Html(
        'Rich Description', translate=True, sanitize=False
    )
