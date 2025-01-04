from collections import defaultdict

from odoo import api, fields, models

from .. import const
from ..utils.fitter import calc_raw_sheet_quantity
from ..value_objects import sheet as vo_sheet


def filter_by_component(recs, component):
    return recs.filtered(lambda r: r.component_id == component)


class PackageConfiguratorCirculationItem(models.Model):
    _name = 'package.configurator.circulation.item'
    _description = "Package Configurator Circulation Component"

    circulation_id = fields.Many2one(
        'package.configurator.circulation',
        required=True,
        ondelete='cascade',
    )
    component_id = fields.Many2one(
        'package.configurator.component',
        required=True,
        ondelete='cascade',
    )
    quantity = fields.Integer(compute='_compute_quantity', help="Raw Sheets Quantity")
    print_unit_cost = fields.Float(
        digits=const.DecimalPrecision.COST,
        compute='_compute_print_unit_cost',
    )
    stamp_cost = fields.Float(
        digits=const.DecimalPrecision.COST,
        compute='_compute_stamp_cost',
    )
    foil_cost = fields.Float(
        digits=const.DecimalPrecision.COST,
        compute='_compute_foil_cost',
    )
    circulation_setup_ids = fields.One2many(
        'package.configurator.circulation.item.setup',
        'circulation_item_id',
    )

    @api.depends(
        'circulation_id.configurator_id.component_ids.component_type',
        'circulation_id.configurator_id.component_ids.sheet_id',
        'circulation_id.configurator_id.component_ids.fit_qty',
        'circulation_id.quantity',
    )
    def _compute_quantity(self):
        circulations = self.mapped('circulation_id')
        for circ in circulations:
            data = self._get_quantity_data(circ)
            for circ_comp, qty in data.items():
                circ_comp.quantity = qty

    @api.depends(
        'circulation_id.configurator_id.component_ids.sheet_id',
        'circulation_id.configurator_id.component_ids.print_color_id',
        'circulation_id.quantity',
        'quantity',
    )
    def _compute_print_unit_cost(self):
        circulations = self.mapped('circulation_id')
        for circ in circulations:
            data = self._get_print_unit_cost_data(circ)
            for circ_comp, unit_cost in data.items():
                circ_comp.print_unit_cost = unit_cost

    @api.depends(
        'circulation_id.configurator_id.cfg_stamp_ids.component_id',
        'circulation_id.configurator_id.cfg_stamp_ids.stamp_id',
        'circulation_id.quantity',
    )
    def _compute_stamp_cost(self):
        for rec in self:
            cfg = rec.circulation_id.configurator_id
            qty = rec._get_foil_stamp_raw_qty()
            cfg_stamps = filter_by_component(cfg.cfg_stamp_ids, rec.component_id)
            tool_cost = sum(cs.stamp_id.tool_cost for cs in cfg_stamps)
            foil_cost = sum(
                cs.stamp_id.unit_cost * qty
                for cs in cfg_stamps
                if cs.stamp_id.with_foil
            )
            rec.stamp_cost = tool_cost + foil_cost

    @api.depends(
        'circulation_id.configurator_id.cfg_foil_ids.component_id',
        'circulation_id.configurator_id.cfg_foil_ids.foil_id',
        'circulation_id.quantity',
    )
    def _compute_foil_cost(self):
        for rec in self:
            cfg = rec.circulation_id.configurator_id
            qty = rec._get_foil_stamp_raw_qty()
            cfg_foils = filter_by_component(cfg.cfg_foil_ids, rec.component_id)
            form_cost = sum(cf.foil_id.form_cost for cf in cfg_foils)
            # Cost of material itself
            film_cost = sum(cf.foil_id.unit_cost * qty for cf in cfg_foils)
            rec.foil_cost = form_cost + film_cost

    def action_open_circulation_setups(self):
        self.ensure_one()
        action = (
            self.env['ir.actions.act_window']
            .sudo()
            ._for_xml_id(
                'package_configurator.'
                + 'package_configurator_circulation_item_setup_action'
            )
        )
        action.update(
            {
                'context': {'default_circulation_item_id': self.id},
                'domain': [('circulation_item_id', '=', self.id)],
            }
        )
        return action

    def _get_quantity_data(self, circ):
        data = self._get_init_quantity_data(circ)
        circ_items = circ.item_ids
        qty_map = defaultdict(list)
        for item in circ_items:
            component = item.component_id
            if not component.fit_qty:
                continue
            sheet = component.sheet_id
            # min_qty of course is the same, but using it to later
            # retrieve it when building SheetQuantity!
            qty_map[(sheet.id, sheet.min_qty)].append(
                vo_sheet.SheetQuantityItem(
                    # Mapping by circ_item record!
                    code=item,
                    fit_qty=component.fit_qty,
                    setup_raw_qty=sum(
                        s.setup_raw_qty for s in item.circulation_setup_ids
                    ),
                )
            )
        sheets = []
        for (__, min_qty), items in qty_map.items():
            sheets.append(vo_sheet.SheetQuantity(min_qty=min_qty, items=items))
        data.update(self.env['package.sheet.quantity'].calc(circ.quantity, sheets))
        return data

    def _get_init_quantity_data(self, circ):
        return {ci: 0 for ci in circ.item_ids}

    def _get_print_unit_cost_data(self, circ):
        data = self._get_init_print_unit_cost_data(circ)
        pricelist = circ.configurator_id.print_house_id.print_pricelist_id
        if not pricelist:
            return data
        circ_items = circ.item_ids
        sheet_color_map = defaultdict(lambda: self.browse())
        for item in circ_items:
            component = item.component_id
            color = component.print_color_id
            if not color:
                continue
            # Grouping by sheet/color to be able to use total quantity
            # of grouped items. This way cost is more optimized as
            # we don't isolate each component cost if same material
            # and color would be used for multiple components!
            sheet_color_map[(item.component_id.sheet_id, color)] |= item
        for (_sheet, color), items in sheet_color_map.items():
            quantity = sum(item.quantity for item in items)
            unit_cost = pricelist.match_rule(color, quantity).unit_cost
            data.update({item: unit_cost for item in items})
        return data

    def _get_init_print_unit_cost_data(self, circ):
        return {ci: 0.0 for ci in circ.item_ids}

    def _get_foil_stamp_raw_qty(self):
        self.ensure_one()
        comp = self.component_id
        qty = calc_raw_sheet_quantity(self.circulation_id.quantity, comp.fit_qty)
        # We also need to include its setup quantity
        circ_setups = self._get_circ_item_setups(const.SetupType.FOIL)
        setup_qty = sum(circ_setup.setup_raw_qty for circ_setup in circ_setups)
        return qty + setup_qty

    def _get_circ_item_setups(self, setup_type: const.SetupType):
        self.ensure_one()
        return self.circulation_setup_ids.filtered(
            lambda r: r.setup_id.setup_type == setup_type
        )
