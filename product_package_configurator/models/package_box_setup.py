from odoo import fields, models

from .. import const
from ..value_objects.layout import Layout2D

HELP_NO_LIMIT = "0 means no limit"


class PackageBoxSetup(models.Model):
    """Model to tell how much specific sheet is needed for setup (wastage)."""

    _name = 'package.box.setup'
    _description = "Package Box Setup"
    _order = "sequence, id"

    @property
    def _rules_ordered(self):
        self.ensure_one()
        # Doing search, so we would get rules ordered.
        return self.env['package.box.setup.rule'].search([('setup_id', '=', self.id)])

    name = fields.Char(required=True)
    setup_type = fields.Selection([(const.SetupType.SHEET, "Sheet")], required=True)
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many('package.box.setup.rule', 'setup_id', string="Rules")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    # Constrains limiting this setup usage.
    box_type_ids = fields.Many2many(
        'package.box.type',
        'package_box_setup_box_type_rel',
        'setup_id',
        'box_type_id',
        string="Box Types",
        help="Box types that can use this setup. If left empty, it means all box "
        + "types can use it.",
    )
    min_layout_length = fields.Float("Minimum Layout Length (mm)", help=HELP_NO_LIMIT)
    min_layout_width = fields.Float("Minimum Layout Width (mm)", help=HELP_NO_LIMIT)
    max_layout_length = fields.Float("Maximum Layout Length (mm)", help=HELP_NO_LIMIT)
    max_layout_width = fields.Float("Maximum Layout Width (mm)", help=HELP_NO_LIMIT)

    def match_setup_rule(
        self, box_qty: int, layout: Layout2D | None = None, box_type=None
    ):
        """Match setup rule by scanning setups and their rules."""
        for setup in self:
            if not setup._match_setup(layout=layout, box_type=box_type):
                continue
            for rule in setup._rules_ordered:
                if rule.match_rule(box_qty):
                    return rule
        return self.env['package.box.setup.rule']

    def _match_setup(self, layout: Layout2D | None = None, box_type=None):
        self.ensure_one()
        if layout is not None and not self._match_layout(layout):
            return False
        if box_type is not None and not self._match_box_type(box_type):
            return False
        return True

    def _match_layout(self, layout):
        def match_min(fname, value):
            min_ = self[fname]
            return not min_ or value >= self[fname]

        def match_max(fname, value):
            max_ = self[fname]
            return not max_ or value <= self[fname]

        self.ensure_one()
        return (
            match_min('min_layout_length', layout.length)
            and match_min('min_layout_width', layout.width)
            and match_max('max_layout_length', layout.length)
            and match_max('max_layout_width', layout.width)
        )

    def _match_box_type(self, box_type):
        self.ensure_one()
        return not self.box_type_ids or box_type in self.box_type_ids
