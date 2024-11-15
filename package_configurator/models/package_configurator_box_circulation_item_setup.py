from collections import defaultdict

from odoo import api, fields, models

from .. import const
from ..utils.fitter import calc_sheet_quantity
from ..value_objects.layout import Layout2D


class PackageConfiguratorBoxCirculationItemSetup(models.Model):
    _name = 'package.configurator.box.circulation.item.setup'
    _description = "Package Configurator Box Circulation Component Setup"

    circulation_item_id = fields.Many2one(
        'package.configurator.box.circulation.item',
        required=True,
        ondelete='cascade',
    )
    setup_rule_id = fields.Many2one('package.box.setup.rule', required=True)
    setup_id = fields.Many2one(related='setup_rule_id.setup_id')
    setup_raw_qty = fields.Integer(
        "Raw Setup Quantity", compute='_compute_setup_raw_qty'
    )

    @api.depends(
        'circulation_item_id.component_id.fit_qty',
        'setup_rule_id',
    )
    def _compute_setup_raw_qty(self):
        for rec in self:
            component = rec.circulation_item_id.component_id
            setup_raw_qty = 0
            fit_qty = component.fit_qty
            if fit_qty:
                setup_raw_qty = calc_sheet_quantity(
                    rec.setup_rule_id.setup_qty, fit_qty
                )
            rec.setup_raw_qty = setup_raw_qty

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
                circ.quantity, layout=layout, box_type=circ.configurator_id.box_type_id
            )
            if setup_rule:
                vals_list.append(self._prepare_ciculation_setup(circ_item, setup_rule))
        return vals_list

    def _is_circ_item_need_setup(self, circ_item, setup_type, setups):
        if (
            setup_type == const.SetupType.PRINT
            # If component has no color selected, it means, no setup is needed for it.
            # PRINT is valid when it is used only on some components, but not all!
            and not circ_item.component_id.print_color_id
        ):
            return False
        return True

    @api.model
    def _prepare_ciculation_setup(self, circulation_item, setup_rule):
        return {
            'circulation_item_id': circulation_item.id,
            'setup_rule_id': setup_rule.id,
        }
