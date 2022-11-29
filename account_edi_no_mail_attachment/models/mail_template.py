from odoo import models

from .res_config_settings import CFG_PARAM_NO_EDI_IN_MAIL


class MailingTemplate(models.Model):
    """Extend to disable edi attachments in mail."""

    _inherit = 'mail.template'

    def _get_edi_attachments(self, document):
        if (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_NO_EDI_IN_MAIL)
        ):
            return []
        return super()._get_edi_attachments(document)
