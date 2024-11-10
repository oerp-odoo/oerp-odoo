from odoo import api, fields, models
from odoo.fields import Command

from .. import const
from ..utils.misc import multiply


class PackageConfiguratorBoxCirculation(models.Model):
    """Model to be able to have multiple circulation options for box."""

    _name = 'package.configurator.box.circulation'
    _inherit = 'package.configurator.circulation'
    _description = "Package Configurator Box Circulation"

    configurator_id = fields.Many2one('package.configurator.box')
    item_ids = fields.One2many(
        'package.configurator.box.circulation.item',
        'circulation_id',
        store=True,
        compute='_compute_item_ids',
    )
    total_lamination_inside_cost = fields.Float(
        compute='_compute_lamination_cost', digits=const.DecimalPrecision.COST
    )
    total_lamination_outside_cost = fields.Float(
        compute='_compute_lamination_cost', digits=const.DecimalPrecision.COST
    )
    # price/cost fields should be part of package.configurator.circulation
    # abstraction, which would need to be implemented in concrete class.
    unit_cost = fields.Float(
        compute='_compute_cost', digits=const.DecimalPrecision.COST
    )
    total_cost = fields.Float(
        compute='_compute_cost', digits=const.DecimalPrecision.COST
    )

    @api.depends('configurator_id.component_ids')
    def _compute_item_ids(self):
        for rec in self:
            components = rec.configurator_id.component_ids
            data = []
            for component in components:
                data.append(Command.create({'component_id': component.id}))
            rec.item_ids = data

    @api.depends(
        'configurator_id.component_ids.fit_qty',
        'quantity',
    )
    def _compute_sheet_quantity(self):
        for rec in self:
            rec.update(rec._get_sheet_quantity_data())

    @api.depends(
        'quantity',
        'configurator_id.lamination_inside_unit_cost',
        'configurator_id.lamination_outside_unit_cost',
    )
    def _compute_lamination_cost(self):
        for rec in self:
            cfg = rec.configurator_id
            rec.update(
                {
                    'total_lamination_inside_cost': (
                        rec.quantity * cfg.lamination_inside_unit_cost
                    ),
                    'total_lamination_outside_cost': (
                        rec.quantity * cfg.lamination_outside_unit_cost
                    ),
                }
            )

    @api.depends(
        'quantity',
        'total_lamination_inside_cost',
        'total_lamination_outside_cost',
        'item_ids.quantity',
        'item_ids.circulation_setup_ids.setup_raw_qty',
    )
    def _compute_cost(self):
        for rec in self:
            rec.update(rec._get_price_data())

    def create_circulation_setups(self, setups):
        self.mapped('item_ids.circulation_setup_ids').unlink()
        CirculationItemSetup = self.env[
            'package.configurator.box.circulation.item.setup'
        ]
        vals_list = []
        for circ_item in self.item_ids:
            vals_list.extend(
                CirculationItemSetup.prepare_circulation_setups(circ_item, setups)
            )
        if vals_list:
            CirculationItemSetup.create(vals_list)
        return True

    def _get_price_data(self):
        self.ensure_one()
        data = {'unit_cost': 0, 'total_cost': 0}
        if not self.quantity:
            return data
        total_cost = 0
        for item in self.item_ids:
            unit_cost = item.component_id.sheet_id.unit_cost
            total_cost += multiply(unit_cost, item.quantity)
        total_cost += self.total_lamination_inside_cost
        total_cost += self.total_lamination_outside_cost
        data.update({'unit_cost': total_cost / self.quantity, 'total_cost': total_cost})
        return data
