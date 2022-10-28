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
    def get_main_rule(self, lines_obj, product_fname='product_id'):
        """Find main rule from given lines_obj.

        Rule is searched by iterating over all existing rules and
        returning first one that matches product between rule and line
        object. If no rule is found, fallback is returned, if one was
        set.

        Args:
            lines_obj (any): can be any object that is iterated having
                product attribute defined.
            product_fname (str): field name to use on lines_obj to
                retrieve related product.

        """
        for rule in self._rules:
            for line in lines_obj:
                line_product = getattr(line, product_fname)
                if rule.product_id == line_product:
                    return rule
        return self._fallback_rule
