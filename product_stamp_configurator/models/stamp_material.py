from odoo import fields, models


class StampMaterial(models.Model):

    _name = 'stamp.material'
    _description = "Stamp Material"

    name = fields.Char(required=True)
    label = fields.Char(help="Generic Name", required=True)
    code = fields.Char("Symbol", required=True)
    thickness = fields.Float("Thickness, mm")
    product_id = fields.Many2one('product.product', "Raw Material")
    price = fields.Float("Price per Square Meter")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
