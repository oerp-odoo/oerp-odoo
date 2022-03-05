from odoo import models, fields


class ResCompany(models.Model):
    """Extend to add field vies_autofill."""

    _inherit = 'res.company'

    vies_autofill = fields.Boolean(string="VIES Autofill")
