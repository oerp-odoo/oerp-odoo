from odoo import fields, models

from .res_config_settings import CFG_PARAM_NO_CREATE


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_rel_field_quick_create_disabled = fields.Boolean(
        compute='_compute_context_rel_field_quick_create_disabled',
    )

    def _compute_context_rel_field_quick_create_disabled(self):
        is_enabled = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_NO_CREATE)
        )
        self.update(
            {'context_rel_field_quick_create_disabled': bool(is_enabled)}
        )
