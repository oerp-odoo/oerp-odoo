from odoo import fields, models


class ResCompany(models.Model):
    """Extend to add fields note_b2c, note_b2b."""

    _inherit = 'res.company'

    note_b2c = fields.Text("Business to Customer Note", translate=True)
    note_b2b = fields.Text("Business to Business Note", translate=True)
