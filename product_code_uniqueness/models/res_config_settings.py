from odoo import fields, models

CFG_PARAM_PRODUCT_CODE_UNIQUE = 'product_code_uniqueness.code_unique'


class ResConfigSettings(models.TransientModel):
    """Extend with product code case-(in)sensitive uniqueness option."""

    _inherit = 'res.config.settings'

    product_code_unique = fields.Selection(
        [
            ('disabled', "Disabled"),
            ('enabled', "Enabled"),
            ('enabled_insensitive', "Enabled Case-Insensitive"),
        ],
        string="Unique Product Codes",
        config_parameter=CFG_PARAM_PRODUCT_CODE_UNIQUE,
        help="Check this if Product Code's (Internal Reference) Uniqueness "
        "should be enabled.",
        default='disabled',
    )
