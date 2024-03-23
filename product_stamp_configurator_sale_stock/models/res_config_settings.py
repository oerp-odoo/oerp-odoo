from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_route_stamp_default_ids = fields.Many2many(
        comodel_name='stock.route',
        compute='_compute_stock_route_stamp_default_ids',
        inverse='_inverse_stock_route_stamp_default_ids',
        domain=[('product_selectable', '=', True)],
    )

    @api.depends('company_id.stock_route_stamp_default_ids')
    def _compute_stock_route_stamp_default_ids(self):
        for rec in self:
            rec.stock_route_stamp_default_ids = (
                rec.company_id.stock_route_stamp_default_ids
            )

    def _inverse_stock_route_stamp_default_ids(self):
        for rec in self:
            rec.company_id.stock_route_stamp_default_ids = (
                rec.stock_route_stamp_default_ids
            )
