from collections import defaultdict

from odoo import api, fields, models

from .. import const
from ..value_objects import layout as vo_layout


class PackageConfiguratorCirculationLabor(models.Model):
    _name = 'package.configurator.circulation.labor'
    _description = "Package Configurator Circulation Labor"
    _order = "labor_id, id"

    circulation_id = fields.Many2one('package.configurator.circulation', required=True)
    labor_id = fields.Many2one('package.labor', required=True)
    hour_profit = fields.Float(
        "Labor Profit per Hour", digits=const.DecimalPrecision.PRICE
    )
    process_ids = fields.One2many(
        'package.configurator.circulation.labor.process',
        'circulation_labor_id',
    )
    total_labor_hours = fields.Float(
        digits=const.DecimalPrecision.MEASURE, compute='_compute_labor_data'
    )
    unit_cost = fields.Float(
        digits=const.DecimalPrecision.COST, compute='_compute_labor_data'
    )
    total_cost = fields.Float(
        digits=const.DecimalPrecision.COST, compute='_compute_labor_data'
    )
    unit_profit = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_labor_data'
    )
    total_profit = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_labor_data'
    )
    total_price = fields.Float(
        digits=const.DecimalPrecision.PRICE, compute='_compute_labor_data'
    )

    @api.depends(
        'labor_id',
        'hour_profit',
        'process_ids.total_cost',
        'process_ids.total_labor_hours',
        'process_ids.total_profit',
        'process_ids.unit_profit',
        'process_ids.total_price',
    )
    def _compute_labor_data(self):
        for rec in self:
            total_labor_hours = unit_cost = total_cost = 0.0
            unit_profit = total_profit = total_price = 0.0
            for p in rec.process_ids:
                total_labor_hours += p.total_labor_hours
                total_cost += p.total_cost
                unit_cost += p.unit_cost
                unit_profit += p.unit_profit
                total_profit += p.total_profit
                total_price += p.total_price
            rec.update(
                {
                    'total_labor_hours': total_labor_hours,
                    'total_cost': total_cost,
                    'unit_cost': unit_cost,
                    'total_profit': total_profit,
                    'unit_profit': unit_profit,
                    'total_price': total_price,
                }
            )

    @api.model
    def prepare_labors(self, circ):
        labors = self.env['package.labor'].search([])
        CircLaborProcess = self.env['package.configurator.circulation.labor.process']
        labor_groups = self._group_labors_with_component_type(labors, circ)
        vals_list = []
        for labor, comp_type_codes in labor_groups.items():
            process_vals_list = CircLaborProcess.prepare_labor_processes(
                labor, circ, comp_type_codes
            )
            # If we found not processes, there is no point to create circulation labor!
            if not process_vals_list:
                continue
            vals_list.append(
                {
                    'labor_id': labor.id,
                    'hour_profit': labor.default_hour_profit,
                    'circulation_id': circ.id,
                    'process_ids': [(0, 0, v) for v in process_vals_list],
                }
            )
        return vals_list

    def action_open_circulation_labor_processes(self):
        self.ensure_one()
        action = (
            self.env['ir.actions.act_window']
            .sudo()
            ._for_xml_id(
                'package_configurator.'
                + 'package_configurator_circulation_labor_process_action'
            )
        )
        action.update(
            {
                'context': {'default_circulation_labor_id': self.id},
                'domain': [('circulation_labor_id', '=', self.id)],
            }
        )
        return action

    def _group_labors_with_component_type(self, labors, circ):
        groups = defaultdict(set)
        for comp in circ.configurator_id.component_ids:
            labor = labors.match_labor(
                self.circulation_id.quantity,
                vo_layout.Layout2D(
                    length=comp.component_length, width=comp.component_width
                ),
            )
            if not labor:
                continue
            groups[labor].add(comp.component_type_id.code)
        return groups
