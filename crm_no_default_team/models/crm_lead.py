from odoo import models

from ..const import CFG_PARAM_NO_DEFAULT_TEAM


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _compute_team_id(self):
        if self.env['ir.config_parameter'].sudo().get_param(CFG_PARAM_NO_DEFAULT_TEAM):
            return
        return super()._compute_team_id()
