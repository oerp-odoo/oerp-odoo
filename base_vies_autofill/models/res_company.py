from odoo import fields, models


class ResCompany(models.Model):
    """Extend to add field vies_autofill."""

    _inherit = 'res.company'

    vies_autofill = fields.Boolean(string="VIES Autofill")
