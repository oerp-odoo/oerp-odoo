from odoo import api, fields, models


class StampDesign(models.Model):

    _name = 'stamp.design'
    _description = "Stamp Design Type"

    name = fields.Char(required=True)
    code = fields.Char("Design Type", required=True)
    category_id = fields.Many2one(
        'product.category',
        required=True,
        domain=[('stamp_type', '=', 'die')],
    )
    is_embossed = fields.Boolean(help="Actual for embossed design pricing")
    design_base_embossed_id = fields.Many2one(
        'stamp.design', "Base for Embossed Design"
    )
    engraving_speed = fields.Integer(help="Engraving speed (min/100 sqcm)")
    weight_coefficient = fields.Float()
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    # TODO: cache it.
    @api.model
    def get_design_codes(self, company_id):
        return tuple(self.search([('company_id', '=', company_id)]).mapped('code'))
