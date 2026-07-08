from odoo import fields, models

from ..const import CFG_PARAM_SALE_NAME_UNIQ


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_name_unique = fields.Boolean(
        string="Unique Sale Order Number", config_parameter=CFG_PARAM_SALE_NAME_UNIQ
    )
