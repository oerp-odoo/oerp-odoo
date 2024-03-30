from odoo import api, models

from ..models.res_config_settings import CFG_PARAM_SPLIT_MODE


class MrpProductionSplitWizard(models.TransientModel):
    _inherit = 'mrp.production.split.wizard'
    _description = "Manufacturing Orders Split"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        split_mode = (
            self.env['ir.config_parameter'].sudo().get_param(CFG_PARAM_SPLIT_MODE)
        )
        if split_mode:
            res['split_mode'] = split_mode
        return res
