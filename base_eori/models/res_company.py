from odoo import models, fields


class ResCompany(models.Model):
    """Extend to eori related field."""

    _inherit = 'res.company'

    eori = fields.Char(related='partner_id.eori', readonly=False)
