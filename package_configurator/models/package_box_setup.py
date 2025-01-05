from odoo import fields, models

from .. import const
from ..utils.fitter import calc_raw_sheet_quantity
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
    setup_type = fields.Selection(
        const.SETUP_TYPE_SELECTION,
        required=True,
    )
    setup_qty_mode = fields.Selection(
        [('fixed', "Fixed"), ('relative', "Relative")],
        string="Setup Quantity Mode",
        required=True,
        default='fixed',
        help="* Fixed: use defined setup quantity on rule\n* Relative: calculate"
        " proportional quantity from the matched rule to the next role.",
    )
    setup_qty_measure = fields.Selection(
        [('cut_sheet', "Cut Sheet"), ('raw_sheet', "Raw Sheet")],
        required=True,
        string="Setup Quantity Measure",
        default='cut_sheet',
        help="How to measure Setup Quantity on rules",
    )
    inp_qty_measure = fields.Selection(
        # Box here means unconverted quantity coming from circulation which is boxes,
        # but in reality it would be quantity of specific component of a box!
        [('box', "Box"), ('raw_sheet', "Raw Sheet")],
        required=True,
        string="Input Quantity Measure",
        default='box',
        help="How to measure Input Quantity on rules. "
        + "Minimum Quantity must match the measure!",
    )
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many('package.box.setup.rule', 'setup_id', string="Rules")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    # Constrains limiting this setup usage.
    package_kind_ids = fields.Many2many(
        'package.kind',
        'package_setup_package_kind_rel',
        'setup_id',
        'package_kind_id',
        string="Package Kinds",
        help="Package Kinds that can use this setup. If left empty, it means all kinds "
        + "can use it.",
    )
    min_layout_length = fields.Float("Minimum Layout Length (mm)", help=HELP_NO_LIMIT)
    min_layout_width = fields.Float("Minimum Layout Width (mm)", help=HELP_NO_LIMIT)
    max_layout_length = fields.Float("Maximum Layout Length (mm)", help=HELP_NO_LIMIT)
    max_layout_width = fields.Float("Maximum Layout Width (mm)", help=HELP_NO_LIMIT)

    def convert_inp_qty(self, qty: int, fit_qty: int):
        """Calc real input qty when quantity of boxes/components is known."""
        self.ensure_one()
        if self.inp_qty_measure == 'box':
            return qty
        try:
            return calc_raw_sheet_quantity(qty, fit_qty)
        except ZeroDivisionError:
            return 0

    def match_setup_rule(
        self,
        quantity: int,
        fit_qty: int,
        component_type=None,
        layout: Layout2D | None = None,
        box_type=None,
    ):
        """Match setup rule by scanning setups and their rules.

        Args:
            quantity: quantity of boxes or components
            fit_qty: number of specific component that fits on raw sheet.
            component_type: which component to match in setup rules if any.
            layout: layout to match in setup if any.
            box_type: whether box_type must match on setup.

        """
        for setup in self:
            if not setup._match_setup(layout=layout, box_type=box_type):
                continue
            inp_qty = setup.convert_inp_qty(quantity, fit_qty)
            for rule in setup._rules_ordered:
                if rule.match_rule(inp_qty, component_type=component_type):
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
        return not self.package_kind_ids or box_type in self.package_kind_ids
