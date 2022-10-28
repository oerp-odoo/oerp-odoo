from odoo import models, fields


class ProductTemplate(models.Model):
    """Extend to add description_rich_invoice field."""

    _inherit = 'product.template'

    description_rich_invoice = fields.Html(
        'Invoices Rich Description', translate=True, sanitize=False
    )
