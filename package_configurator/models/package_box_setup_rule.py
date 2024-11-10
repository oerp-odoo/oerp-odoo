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
    setup_qty = fields.Integer(
        "Setup Quantity",
        # NOTE. This is quantity for prepared material, like cut sheet, not the whole
        # raw sheet!
        help="Material wastage quantity used when doing setup",
        required=True,
    )

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
