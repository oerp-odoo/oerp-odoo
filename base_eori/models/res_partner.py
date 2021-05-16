from odoo import models, fields, api


class ResPartner(models.Model):
    """Extend to eori field."""

    _inherit = 'res.partner'

    eori = fields.Char(
        string="EORI",
        help="Economic Operators Registration and Identification number"
    )

    @api.model
    def _commercial_fields(self):
        """Extend to add eori field."""
        return super()._commercial_fields() + ['eori']
