from odoo import fields, models


class StampDesign(models.Model):

    _name = 'stamp.design'
    _description = "Stamp Design Type"

    name = fields.Char(required=True)
    code = fields.Char("Design Type", required=True)
    category_id = fields.Many2one('product.category', required=True)
    is_embossed = fields.Boolean(help="Actual for embossed design pricing")
    design_base_embossed_id = fields.Many2one(
        'stamp.design', "Base for Embossed Design"
    )
    engraving_speed = fields.Integer(help="Engraving speed (min/100 sqcm)")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
