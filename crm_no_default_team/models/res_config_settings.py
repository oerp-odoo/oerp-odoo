from odoo import fields, models

from ..const import CFG_PARAM_NO_DEFAULT_TEAM


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_no_default_team = fields.Boolean(
        string="No Default Team for Lead/Opportunity",
        config_parameter=CFG_PARAM_NO_DEFAULT_TEAM,
    )
