from odoo import fields, models

CFG_PARAM_SALE_NAME_UNIQ = 'sale_name_unique.enabled'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_name_unique = fields.Boolean(
        string="Unique Sale Order Number", config_parameter=CFG_PARAM_SALE_NAME_UNIQ
    )
