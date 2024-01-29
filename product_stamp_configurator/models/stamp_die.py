from odoo import fields, models


class StampDie(models.Model):

    _name = 'stamp.die'
    _description = "Stamp Die Type"

    name = fields.Char(required=True, translate=True)
    # Optional if it needs to be included in generated product code.
    code = fields.Char()
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
