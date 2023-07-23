from odoo import fields, models


class ResCompany(models.Model):
    """Extend to eori related field."""

    _inherit = 'res.company'

    eori = fields.Char(related='partner_id.eori', readonly=False)
