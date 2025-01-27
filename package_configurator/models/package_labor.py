from odoo import fields, models

from .. import const
from ..utils.misc import match_max, match_min
from ..value_objects.layout import Layout2D


class PackageLabor(models.Model):
    _name = 'package.labor'
    _description = "Package Labor"
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    hour_cost = fields.Float(string="Cost per Hour", digits=const.DecimalPrecision.COST)
    default_hour_profit = fields.Float(
        "Default Profit per Hour", digits=const.DecimalPrecision.COST
    )
    item_ids = fields.One2many('package.labor.item', 'labor_id')
    min_qty = fields.Integer(
        "Minimum Quantity",
        help="Minimum quantity to use this. 0 means there is no minimum quantity "
        + "limit.",
    )
    max_qty = fields.Integer(
        "Maximum Quantity",
        help="Maximum quantity to use this. 0 means there is no minimum quantity "
        + "limit.",
    )
    min_layout_length = fields.Float(
        "Minimum Layout Length (mm)", help=const.HELP_NO_LIMIT
    )
    min_layout_width = fields.Float(
        "Minimum Layout Width (mm)", help=const.HELP_NO_LIMIT
    )
    max_layout_length = fields.Float(
        "Maximum Layout Length (mm)", help=const.HELP_NO_LIMIT
    )
    max_layout_width = fields.Float(
        "Maximum Layout Width (mm)", help=const.HELP_NO_LIMIT
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    # TODO: use monetary widget on money related fields.
    currency_id = fields.Many2one(related='company_id.currency_id')
    active = fields.Boolean(default=True)

    def match_labor(self, quantity: int, layout: Layout2D):
        for labor in self:
            if labor._match_labor(quantity, layout):
                return labor
        return self.browse()

    def _match_labor(self, quantity: int, layout: Layout2D):
        self.ensure_one()
        return (
            self._match_layout(layout)
            and match_min(self, 'min_qty', quantity)
            and match_max(self, 'max_qty', quantity)
        )

    def _match_layout(self, layout: Layout2D):
        self.ensure_one()
        return (
            match_min(self, 'min_layout_length', layout.length)
            and match_min(self, 'min_layout_width', layout.width)
            and match_max(self, 'max_layout_length', layout.length)
            and match_max(self, 'max_layout_width', layout.width)
        )
