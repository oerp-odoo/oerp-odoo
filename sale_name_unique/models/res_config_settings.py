from odoo import fields, models

CFG_PARAM_SALE_NAME_UNIQ = 'sale_name_unique.enabled'
CFG_PARAM_SALE_NAME_UNIQ_SCOPE = 'sale_name_unique.scope'
DEFAULT_SCOPE = 'company'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_name_unique = fields.Boolean(
        string="Unique Sale Order Number", config_parameter=CFG_PARAM_SALE_NAME_UNIQ
    )
    sale_name_unique_scope = fields.Selection(
        [('company', "Per Company"), ('global', "Globally")],
        string="Unique Sale Order Number Scope",
        config_parameter=CFG_PARAM_SALE_NAME_UNIQ_SCOPE,
        default=DEFAULT_SCOPE,
    )
