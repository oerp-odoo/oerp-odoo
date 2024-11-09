from collections import defaultdict

from odoo import api, fields, models

from ..value_objects import sheet as vo_sheet


class PackageConfiguratorBoxCirculationComponent(models.Model):
    """Class to manage components for each circulation."""

    _name = 'package.configurator.box.circulation.component'
    _description = "Package Configurator Box Circulation Component"

    circulation_id = fields.Many2one(
        'package.configurator.box.circulation', required=True
    )
    component_id = fields.Many2one(
        'package.configurator.box.component',
        required=True,
    )
    quantity = fields.Integer(
        compute='_compute_quantity',
    )

    @api.depends(
        'circulation_id.configurator_id.component_ids.component_type',
        'circulation_id.quantity',
    )
    def _compute_quantity(self):
        circulations = self.mapped('circulation_id')
        for circ in circulations:
            data = self._get_quantity_data(circ)
            for circ_comp, qty in data.items():
                circ_comp.quantity = qty

    def _get_quantity_data(self, circ):
        data = self._get_init_quantity_data(circ)
        circ_components = circ.circulation_component_ids
        qty_map = defaultdict(list)
        for circ_component in circ_components:
            component = circ_component.component_id
            if not component.fit_qty:
                continue
            sheet = component.sheet_id
            # min_qty of course is the same, but using it to later
            # retrieve it when building SheetQuantity!
            qty_map[(sheet.id, sheet.min_qty)].append(
                vo_sheet.SheetQuantityItem(
                    # Mapping by circ_component record!
                    code=circ_component,
                    fit_qty=component.fit_qty,
                    # TODO: integrate with setup!
                    setup_raw_qty=0,
                )
            )
        sheets = []
        for (__, min_qty), items in qty_map.items():
            sheets.append(vo_sheet.SheetQuantity(min_qty=min_qty, items=items))
        data.update(self.env['package.sheet.quantity'].calc(circ.quantity, sheets))
        return data

    def _get_init_quantity_data(self, circ):
        return {cc: 0 for cc in circ.circulation_component_ids}
