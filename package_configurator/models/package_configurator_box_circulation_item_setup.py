from odoo import api, fields, models

from ..utils.fitter import calc_sheet_quantity
from ..value_objects.layout import Layout2D


class PackageConfiguratorBoxCirculationItemSetup(models.Model):
    _name = 'package.configurator.box.circulation.item.setup'
    _description = "Package Configurator Box Circulation Component Setup"

    circulation_item_id = fields.Many2one(
        'package.configurator.box.circulation.item',
        required=True,
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
    def prepare_circulation_setups(self, circulation_item, setups):
        # We build list, because later there will be different kind of
        # setups, not just component preparation itself.
        vals_list = []
        component = circulation_item.component_id
        circ = circulation_item.circulation_id
        layout = Layout2D(
            length=component.component_length, width=component.component_width
        )
        setup_rule = setups.match_setup_rule(
            circ.quantity, layout=layout, box_type=circ.configurator_id.box_type_id
        )
        if setup_rule:
            vals_list.append(
                self._prepare_ciculation_setup(circulation_item, setup_rule)
            )
        return vals_list

    @api.model
    def _prepare_ciculation_setup(self, circulation_item, setup_rule):
        return {
            'circulation_item_id': circulation_item.id,
            'setup_rule_id': setup_rule.id,
        }
