from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    stock_route_stamp_default_ids = fields.Many2many(
        'stock.route',
        'stock_route_default_company_rel',
        'company_id',
        'route_id',
    )
