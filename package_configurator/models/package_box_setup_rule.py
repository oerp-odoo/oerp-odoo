import math

from odoo import api, fields, models


class PackageBoxSetupRule(models.Model):
    _name = 'package.box.setup.rule'
    _description = "Package Box Setup Rule"
    _order = "min_qty desc, id"

    name = fields.Char(compute='_compute_name')

    setup_id = fields.Many2one('package.box.setup', required=True, ondelete='cascade')
    min_qty = fields.Integer(
        "Minimum Box Quantity", help="Minimum quantity of boxes to match this rule"
    )
    # TODO: rename to setup_fixed_qty
    setup_qty = fields.Integer(
        "Setup Quantity",
        # NOTE. This is quantity for prepared material, like cut sheet, not the whole
        # raw sheet!
        help="Material wastage quantity used when doing setup",
        required=True,
    )

    @property
    def _greater_rule(self):
        self.ensure_one()
        current_rule = self
        rules = self.setup_id._rules_ordered
        # We start from second rule, because first one won't have any
        # previous one.
        for idx, rule in enumerate(rules[1:], start=1):
            if rule == current_rule:
                try:
                    return rules[idx - 1]
                except IndexError:
                    return self.browse()
        return self.browse()

    @api.depends('setup_id', 'min_qty', 'setup_qty')
    def _compute_name(self):
        for rec in self:
            setup = rec.setup_id
            rec.name = f'{setup.name} ({rec.min_qty}/{rec.setup_qty})'

    _sql_constraints = [
        (
            'min_qty_setup_uniq',
            'unique (min_qty, setup_id)',
            'The Minimum Quantity must be Unique per Setup!',
        )
    ]

    def match_rule(self, box_qty: int):
        self.ensure_one()
        return box_qty >= self.min_qty

    def calc_setup_qty(self, min_qty: int) -> int:
        self.ensure_one()
        if self.setup_id.setup_qty_mode == 'fixed':
            return self.setup_qty
        return self._calc_relative_setup_qty(min_qty)

    def _calc_relative_setup_qty(self, qty: int) -> int:
        self.ensure_one()
        # Greater rule must have higher quantity than current
        greater_rule = self._greater_rule
        if not greater_rule or qty <= self.min_qty:
            return self.setup_qty
        if greater_rule.min_qty <= max(qty, self.min_qty):
            return greater_rule.setup_qty
        rel_min_qty = greater_rule.min_qty - self.min_qty
        rel_setup_qty = greater_rule.setup_qty - self.setup_qty
        ratio = rel_setup_qty / rel_min_qty
        return math.ceil((qty - self.min_qty) * ratio + self.setup_qty)
