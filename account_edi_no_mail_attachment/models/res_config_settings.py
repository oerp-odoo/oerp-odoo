from odoo import models, fields

CFG_PARAM_NO_EDI_IN_MAIL = 'account_no_mail_attachment.no_edi_in_mail'


class ResConfigSettings(models.TransientModel):
    """Extend to add ."""

    _inherit = 'res.config.settings'

    no_edi_in_mail = fields.Boolean(
        string="Exclude EDI attachments from Mail",
        config_parameter=CFG_PARAM_NO_EDI_IN_MAIL,
    )
