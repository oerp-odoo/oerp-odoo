from odoo import fields, models


class PackagePrintPricelist(models.Model):
    _name = 'package.print.pricelist'
    _description = "Package Print Pricelist"

    name = fields.Char(required=True)
    rule_ids = fields.One2many(
        'package.print.pricelist.rule', 'print_pricelist_id', string="Rules"
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    def match_rule(self, color, quantity):
        self.ensure_one()
        for rule in self._find_rules():
            if rule.is_match(color, quantity):
                return rule
        return self.env['package.print.pricelist.rule']

    # TODO: might be better to limit by color as we will be matching rule
    # one color at a time!
    def _find_rules(self):
        return self.env['package.print.pricelist.rule'].search(
            [('print_pricelist_id', '=', self.id)]
        )
