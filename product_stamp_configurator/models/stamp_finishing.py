from odoo import fields, models


class StampFinishing(models.Model):

    _name = 'stamp.finishing'
    _description = "Stamp Special Finishing"

    name = fields.Char(required=True)
    price = fields.Float("Price per Square Meter", required=True)
    code = fields.Char("Art No symbol", required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
