from odoo import models, fields, api


class ProductMainRule(models.Model):
    """Model to find specific product with some related data set."""

    _name = 'product.main.rule'
    _description = "Main Product Rule"
    _order = "sequence, id"

    name = fields.Char()
    product_id = fields.Many2one('product.product', required=True)
    sequence = fields.Integer(default=10)
    is_fallback = fields.Boolean(
        "Fallback Rule",
        help="If checked, will be used if no other rule can be found.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'is_fallback_uniq',
            'unique (is_fallback)',
            'Only one Fallback Rule is allowed !',
        )
    ]

    @property
    def _rules(self):
        return self.search([('is_fallback', '=', False)])

    @property
    def _fallback_rule(self):
        return self.search([('is_fallback', '=', True)])

    @api.model
    def get_main_rule(self, products):
        """Find main rule from given products.

        Rule is searched by iterating over all existing rules and
        returning first one that matches product between rule and line
        object. If no rule is found, fallback is returned, if one was
        set.

        Args:
            products (product.product): products to compare with main
                product rules and look for a match.

        Returns:
            product.main.rule

        """
        for rule in self._rules:
            if rule.product_id in products:
                return rule
        return self._fallback_rule
