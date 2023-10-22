from odoo import fields, models

CFG_PARAM_NO_CREATE = 'web_no_quick_create.no_create'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rel_field_quick_create_disabled = fields.Boolean(
        string="Disable Quick Create",
        help="Disables quick create on form views",
        config_parameter=CFG_PARAM_NO_CREATE,
    )
