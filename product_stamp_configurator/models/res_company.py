from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    category_default_counter_die_id = fields.Many2one(
        'product.category', string="Default Counter-Die Category"
    )
    category_default_mold_id = fields.Many2one(
        'product.category', string="Default Mold Category"
    )
