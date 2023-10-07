from odoo import models, fields

CFG_PARAM_SPLIT_MODE = "mrp_production_split_extended.default_split_mode"


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    mrp_production_default_split_mode = fields.Selection(
        [
            ("simple", "Extract a quantity from the original MO"),
            ("equal", "Extract a quantity into several MOs with equal quantities"),
            ("custom", "Custom"),
        ],
        string="Production Default Split Mode",
        config_parameter=CFG_PARAM_SPLIT_MODE
    )
