from odoo import fields, models


class StampDifficulty(models.Model):

    _name = 'stamp.difficulty'
    _description = "Stamp Difficulty Level"

    name = fields.Char(required=True)
    coefficient = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
