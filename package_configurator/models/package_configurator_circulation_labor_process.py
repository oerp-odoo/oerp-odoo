import dataclasses

from odoo import api, fields, models

from .. import const
from ..utils.labor import calc_labor_hours
from ..utils.misc import multiply


class PackageConfiguratorCirculationLaborProcess(models.Model):
    _name = 'package.configurator.circulation.labor.process'
    _description = "Package Configurator Circulation Labor Process"
    _order = "component_type_id, labor_type_id, name, id"

    name = fields.Char(required=True)
    circulation_labor_id = fields.Many2one(
        'package.configurator.circulation.labor',
        required=True,
        ondelete='cascade',
    )
    labor_type_id = fields.Many2one('package.labor.type', required=True)
    component_type_id = fields.Many2one('package.component.type', required=True)
    units_per_hour = fields.Integer("Units per Hour")
    setup_minutes = fields.Integer()
    total_labor_hours = fields.Float(
        digits=const.DecimalPrecision.MEASURE, compute='_compute_process_data'
    )
    unit_cost = fields.Float(
        digits=const.DecimalPrecision.COST, compute='_compute_process_data'
    )
    total_cost = fields.Float(
        digits=const.DecimalPrecision.COST, compute='_compute_process_data'
    )
    unit_profit = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_process_data'
    )
    total_profit = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_process_data'
    )
    total_price = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_process_data'
    )

    _sql_constraints = [
        (
            'uph_pstv',
            'CHECK (units_per_hour >= 0)',
            "Units per Hour must be greater than 0.",
        )
    ]

    @api.depends(
        'circulation_labor_id.circulation_id.quantity',
        'circulation_labor_id.labor_id',
        'circulation_labor_id.hour_profit',
        'units_per_hour',
        'setup_minutes',
    )
    def _compute_process_data(self):
        for rec in self:
            circ_labor = rec.circulation_labor_id
            qty = circ_labor.circulation_id.quantity
            try:
                total_labor_hours = calc_labor_hours(
                    qty, rec.units_per_hour, rec.setup_minutes
                )
            except ZeroDivisionError:
                total_labor_hours = 0
            total_cost = multiply(circ_labor.labor_id.hour_cost, total_labor_hours)
            total_profit = multiply(circ_labor.hour_profit, total_labor_hours)
            rec.update(
                {
                    'total_labor_hours': total_labor_hours,
                    'total_cost': total_cost,
                    'unit_cost': total_cost / qty,
                    'total_profit': total_profit,
                    'unit_profit': total_profit / qty,
                    'total_price': total_cost + total_profit,
                }
            )

    @api.model
    def prepare_labor_processes(self, labor, circ, comp_type_codes):
        def transform_to_vals(process):
            vals = dataclasses.asdict(process)
            comp_type_code = vals.pop('component_type')
            vals.pop('to_fit')
            labor_type_code = vals.pop('labor_type')
            vals.update(
                {
                    'labor_type_id': self.env['package.labor.type'].get_id(
                        labor_type_code
                    ),
                    'component_type_id': self.env['package.component.type'].get_id(
                        comp_type_code
                    ),
                }
            )
            return vals

        vals_list = []
        processes = self.env['package.labor.process.generation'].generate(
            labor,
            circ.configurator_id,
            component_types=tuple(comp_type_codes),
        )
        for process in processes:
            vals_list.append(transform_to_vals(process))
        return vals_list
