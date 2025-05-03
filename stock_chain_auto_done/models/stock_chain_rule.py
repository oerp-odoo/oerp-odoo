from odoo import fields, models


class StockChainRule(models.Model):
    _name = 'stock.chain.rule'
    _description = "Stock Chain Rule"
    _order = "sequence, id"
    _rec_name = 'location_id'

    location_id = fields.Many2one('stock.location', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    _sql_constraints = [
        (
            'location_uniq',
            'unique (location_id, company_id)',
            'The Location must be unique per Company!',
        )
    ]

    def get_locations(self, company_id):
        domain = self._prepare_domain(company_id)
        return self.search(domain).mapped('location_id')

    def _prepare_domain(self, company_id):
        return [('company_id', '=', company_id)]
