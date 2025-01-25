from odoo import api, fields, models
from odoo.fields import Command

from .. import const
from ..utils.misc import multiply


class PackageConfiguratorCirculation(models.Model):
    """Model to be able to have multiple circulation options for package."""

    _name = 'package.configurator.circulation'
    _description = "Package Configurator Circulation"

    configurator_id = fields.Many2one('package.configurator', required=True)
    quantity = fields.Integer(required=True)
    item_ids = fields.One2many(
        'package.configurator.circulation.item',
        'circulation_id',
        store=True,
        compute='_compute_item_ids',
    )
    total_lamination_cost = fields.Float(
        compute='_compute_total_lamination_cost', digits=const.DecimalPrecision.COST
    )
    unit_cost = fields.Float(
        compute='_compute_cost',
        digits=const.DecimalPrecision.COST,
        recursive=True,
    )
    total_cost = fields.Float(
        compute='_compute_cost',
        digits=const.DecimalPrecision.COST,
        recursive=True,
    )

    @property
    def _total_lamination_cost(self):
        self.ensure_one()
        cost = 0.0
        for cfg_lamination in self.configurator_id.cfg_lamination_ids:
            # area_unit_cost means, one cut sheet.
            cost += self.quantity * cfg_lamination.area_unit_cost
        return cost

    @api.depends('configurator_id.component_ids')
    def _compute_item_ids(self):
        for rec in self:
            rec.item_ids = [Command.clear()]
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
        'configurator_id.cfg_lamination_ids.side',
        'configurator_id.cfg_lamination_ids.lamination_id',
    )
    def _compute_total_lamination_cost(self):
        for rec in self:
            rec.total_lamination_cost = rec._total_lamination_cost

    @api.depends(
        'quantity',
        'total_lamination_cost',
        'item_ids.quantity',
        'item_ids.stamp_cost',
        'item_ids.circulation_setup_ids.setup_raw_qty',
        'configurator_id.configurator_insert_ids.circulation_ids.total_cost',
    )
    def _compute_cost(self):
        for rec in self:
            rec.update(rec._get_cost_data())

    def create_circulation_setups(self, setups):
        self.mapped('item_ids.circulation_setup_ids').unlink()
        CirculationItemSetup = self.env['package.configurator.circulation.item.setup']
        vals_list = []
        for circ_item in self.item_ids:
            vals_list.extend(
                CirculationItemSetup.prepare_circulation_setups(circ_item, setups)
            )
        if vals_list:
            return CirculationItemSetup.create(vals_list)
        return CirculationItemSetup

    def _get_cost_data(self):
        def get_insert_circs(cfg_inserts):
            return cfg_inserts.mapped('circulation_ids').filtered(
                # To include insert circulation, it must match its box circulation!
                lambda r: r.quantity
                == self.quantity
            )

        def get_insert_total_costs(cfg_inserts):
            insert_circs = get_insert_circs(cfg_inserts)
            return sum(ic.total_cost for ic in insert_circs)

        self.ensure_one()
        data = {'unit_cost': 0, 'total_cost': 0}
        if not self.quantity:
            return data
        total_cost = 0
        for item in self.item_ids:
            unit_cost = item.component_id.sheet_id.unit_cost
            total_cost += multiply(unit_cost, item.quantity)
            total_cost += multiply(item.print_unit_cost, item.quantity)
            total_cost += item.stamp_cost
            total_cost += item.foil_cost
        total_cost += self.total_lamination_cost
        cfg_inserts = self.configurator_id.configurator_insert_ids
        if cfg_inserts:
            total_cost += get_insert_total_costs(cfg_inserts)
        data.update({'unit_cost': total_cost / self.quantity, 'total_cost': total_cost})
        return data
