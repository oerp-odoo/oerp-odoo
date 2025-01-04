from collections import defaultdict

from odoo import api, fields, models

from .. import const
from ..utils.fitter import calc_raw_sheet_quantity
from ..value_objects.layout import Layout2D


class PackageConfiguratorCirculationItemSetup(models.Model):
    _name = 'package.configurator.circulation.item.setup'
    _description = "Package Configurator Circulation Component Setup"

    circulation_item_id = fields.Many2one(
        'package.configurator.circulation.item',
        required=True,
        ondelete='cascade',
    )
    setup_rule_id = fields.Many2one('package.box.setup.rule', required=True)
    setup_id = fields.Many2one(related='setup_rule_id.setup_id')
    setup_raw_qty = fields.Integer(
        "Raw Setup Quantity", compute='_compute_setup_raw_qty'
    )

    @property
    def _setup_raw_qty(self):
        self.ensure_one()
        circ_item = self.circulation_item_id
        fit_qty = circ_item.component_id.fit_qty
        if not fit_qty:
            return 0

        inp_qty = self.setup_id.convert_inp_qty(
            circ_item.circulation_id.quantity, fit_qty
        )
        setup_raw_qty = self.setup_rule_id.calc_setup_qty(inp_qty)
        # With raw measure, nothing needs to be converted.
        if self.setup_id.setup_qty_measure == 'raw_sheet':
            return setup_raw_qty
        # Handle `cut` measure.
        # setup quantity on rule is in cut sheets measure, so we convert it to
        # raw measure.
        return calc_raw_sheet_quantity(setup_raw_qty, fit_qty)

    @api.depends(
        'circulation_item_id.component_id.fit_qty',
        'circulation_item_id.circulation_id.quantity',
        'setup_rule_id',
    )
    def _compute_setup_raw_qty(self):
        for rec in self:
            rec.setup_raw_qty = rec._setup_raw_qty

    @api.model
    def prepare_circulation_setups(self, circ_item, setups):
        # We need to prepare setup for each setup type!
        setup_groups = defaultdict(lambda: setups.browse())
        for setup in setups:
            setup_groups[setup.setup_type] |= setup
        vals_list = []
        component = circ_item.component_id
        circ = circ_item.circulation_id
        layout = Layout2D(
            length=component.component_length, width=component.component_width
        )
        for setup_type, sgroup in setup_groups.items():
            if not self._is_circ_item_need_setup(circ_item, setup_type, sgroup):
                continue
            setup_rule = sgroup.match_setup_rule(
                circ.quantity,
                component.fit_qty,
                component_type=component.component_type,
                layout=layout,
                box_type=circ.configurator_id.box_type_id,
            )
            if setup_rule:
                vals_list.append(self._prepare_ciculation_setup(circ_item, setup_rule))
        return vals_list

    def _is_circ_item_need_setup(self, circ_item, setup_type, setups):
        if setup_type == const.SetupType.PRINT:
            return self._is_circ_item_need_print_setup(circ_item)
        if setup_type == const.SetupType.FOIL:
            return self._is_circ_item_need_foil_setup(circ_item)
        return True

    def _is_circ_item_need_print_setup(self, circ_item):
        cfg = circ_item.circulation_id.configurator_id
        # If component has no color selected, it means, no setup is needed for it.
        # PRINT is valid when it is used only on some components, but not all!
        return cfg.print_house_id and circ_item.component_id.print_color_id

    def _is_circ_item_need_foil_setup(self, circ_item):
        comp = circ_item.component_id
        cfg = circ_item.circulation_id.configurator_id
        # foil setup is used for both foil and stamps!
        return bool(
            cfg.cfg_foil_ids.filtered(lambda r: r.component_id == comp)
            or cfg.cfg_stamp_ids.filtered(lambda r: r.component_id == comp)
        )

    @api.model
    def _prepare_ciculation_setup(self, circulation_item, setup_rule):
        return {
            'circulation_item_id': circulation_item.id,
            'setup_rule_id': setup_rule.id,
        }
