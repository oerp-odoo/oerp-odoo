from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Extend to add field vies_autofill."""

    _inherit = 'res.config.settings'

    vies_autofill = fields.Boolean(
        related='company_id.vies_autofill',
        readonly=False,
    )

    @api.onchange('vat_check_vies')
    def _onchange_vat_check_vies(self):
        if not self.vat_check_vies:
            self.vies_autofill = False
