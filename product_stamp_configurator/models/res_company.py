from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    die_default_id = fields.Many2one('stamp.die', string="Default Die Type")
    category_default_counter_die_id = fields.Many2one(
        'product.category',
        string="Default Counter-Die Category",
        domain=[('stamp_type', '=', 'counter_die')],
    )
    category_default_mold_id = fields.Many2one(
        'product.category',
        string="Default Mold Category",
        domain=[('stamp_type', '=', 'mold')],
    )
    quantity_mold_default = fields.Integer(default=1)
