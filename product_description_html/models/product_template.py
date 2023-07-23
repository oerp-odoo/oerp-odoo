from odoo import fields, models


class ProductTemplate(models.Model):
    """Extend to add description_rich_sale field."""

    _inherit = 'product.template'

    description_rich_sale = fields.Html(
        'Sales Rich Description', translate=True, sanitize=False
    )
