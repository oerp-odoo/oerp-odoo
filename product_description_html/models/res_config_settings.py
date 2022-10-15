from odoo import models, fields

RICH_DESCRIPTION_GROUP_XMLID = (
    'product_description_html.product_rich_description_group_use_advanced'
)


class ResConfigSettings(models.TransientModel):
    """Extend to add group_rich_description_use_advanced field."""

    _inherit = 'res.config.settings'

    group_product_rich_description_use_advanced = fields.Boolean(
        string="Use Advanced Product Rich Description",
        implied_group=RICH_DESCRIPTION_GROUP_XMLID,
    )
