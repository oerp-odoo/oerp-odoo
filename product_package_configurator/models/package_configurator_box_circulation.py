from collections import defaultdict

from odoo import api, fields, models
from odoo.fields import Command

from .. import const
from ..utils.misc import multiply
from ..value_objects import sheet as vo_sheet


class PackageConfiguratorBoxCirculation(models.Model):
    """Model to be able to have multiple circulation options for box."""

    _name = 'package.configurator.box.circulation'
    _inherit = 'package.configurator.circulation'
    _description = "Package Configurator Box Circulation"

    configurator_id = fields.Many2one('package.configurator.box')
    circulation_component_ids = fields.One2many(
        'package.configurator.box.circulation.component',
        'circulation_id',
        store=True,
        compute='_compute_circulation_component_ids',
    )
    circulation_setup_ids = fields.One2many(
        'package.configurator.box.circulation.setup',
        'circulation_id',
        string="Setups",
    )
    total_base_greyboard_quantity = fields.Integer(compute='_compute_sheet_quantity')
    total_lid_greyboard_quantity = fields.Integer(compute='_compute_sheet_quantity')
    total_base_inside_wrappingpaper_quantity = fields.Integer(
        compute='_compute_sheet_quantity',
        string="Total Base Inside Wrapping Paper Quantity",
    )
    total_base_outside_wrappingpaper_quantity = fields.Integer(
        compute='_compute_sheet_quantity',
        string="Total Base Outside Wrapping Paper Quantity",
    )
    total_lid_inside_wrappingpaper_quantity = fields.Integer(
        compute='_compute_sheet_quantity',
        string="Total Lid Inside Wrapping Paper Quantity",
    )
    total_lid_outside_wrappingpaper_quantity = fields.Integer(
        compute='_compute_sheet_quantity',
        string="Total Lid Outside Wrapping Paper Quantity",
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
    def _compute_circulation_component_ids(self):
        for rec in self:
            components = rec.configurator_id.component_ids
            data = []
            for component in components:
                data.append(Command.create({'component_id': component.id}))
            rec.circulation_component_ids = data

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
        'total_base_greyboard_quantity',
        'total_base_inside_wrappingpaper_quantity',
        'total_base_outside_wrappingpaper_quantity',
        'total_lid_greyboard_quantity',
        'total_lid_inside_wrappingpaper_quantity',
        'total_lid_outside_wrappingpaper_quantity',
        'quantity',
        'configurator_id.sheet_greyboard_base_id',
        'configurator_id.sheet_greyboard_lid_id',
        'configurator_id.sheet_wrappingpaper_base_inside_id',
        'configurator_id.sheet_wrappingpaper_base_outside_id',
        'configurator_id.sheet_wrappingpaper_lid_inside_id',
        'configurator_id.sheet_wrappingpaper_lid_outside_id',
        'total_lamination_inside_cost',
        'total_lamination_outside_cost',
        'circulation_setup_ids.setup_raw_qty',
    )
    def _compute_cost(self):
        for rec in self:
            rec.update(rec._get_price_data())

    def create_circulation_setups(self, setups):
        # TODO: remove old circ setups!
        self.mapped('circulation_setup_ids').unlink()
        CirculationSetup = self.env['package.configurator.box.circulation.setup']
        # It should be called on same configurator!
        vals_list = []
        for rec in self:
            vals_list.extend(CirculationSetup.prepare_circulation_setups(rec, setups))
        if vals_list:
            CirculationSetup.create(vals_list)
        self.mapped('circulation_component_ids.circulation_setup_ids').unlink()
        CirculationComponentSetup = self.env[
            'package.configurator.box.circulation.component.setup'
        ]
        vals_list = []
        for circ_component in self.circulation_component_ids:
            vals_list.extend(
                CirculationComponentSetup.prepare_circulation_setups(
                    circ_component, setups
                )
            )
        if vals_list:
            CirculationComponentSetup.create(vals_list)
        return True

    def _get_sheet_quantity_data(self):
        def group_sheet_data_if_applicable(
            fit_qty_map, sheet, fit_qty, setup_raw_qty, fname
        ):
            # min_qty of course is the same, but using it to later
            # retrieve it when building SheetQuantity!
            if fit_qty:
                fit_qty_map[(sheet.id, sheet.min_qty)].append(
                    vo_sheet.SheetQuantityItem(
                        code=fname, fit_qty=fit_qty, setup_raw_qty=setup_raw_qty
                    )
                )

        self.ensure_one()
        data = self._get_init_sheet_quantity_data()
        cfg = self.configurator_id
        fit_qty_map = defaultdict(list)
        circ_setups = self.circulation_setup_ids
        comps = cfg.component_ids
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_greyboard_base_id,
            comps.filtered(lambda r: r.component_type == 'base_greyboard').fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.BASE_GREYBOARD
            ).setup_raw_qty,
            'total_base_greyboard_quantity',
        )
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_greyboard_lid_id,
            comps.filtered(lambda r: r.component_type == 'lid_greyboard').fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.LID_GREYBOARD
            ).setup_raw_qty,
            'total_lid_greyboard_quantity',
        )
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_wrappingpaper_base_inside_id,
            comps.filtered(
                lambda r: r.component_type == 'base_wrappingpaper_inside'
            ).fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.BASE_INSIDE_WRAPPING
            ).setup_raw_qty,
            'total_base_inside_wrappingpaper_quantity',
        )
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_wrappingpaper_lid_inside_id,
            comps.filtered(
                lambda r: r.component_type == 'lid_wrappingpaper_inside'
            ).fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.LID_INSIDE_WRAPPING
            ).setup_raw_qty,
            'total_lid_inside_wrappingpaper_quantity',
        )
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_wrappingpaper_base_outside_id,
            comps.filtered(
                lambda r: r.component_type == 'base_wrappingpaper_outside'
            ).fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.BASE_OUTSIDE_WRAPPING
            ).setup_raw_qty,
            'total_base_outside_wrappingpaper_quantity',
        )
        group_sheet_data_if_applicable(
            fit_qty_map,
            cfg.sheet_wrappingpaper_lid_outside_id,
            comps.filtered(
                lambda r: r.component_type == 'lid_wrappingpaper_outside'
            ).fit_qty,
            circ_setups.filtered(
                lambda r: r.part == const.CirculationSetupPart.LID_OUTSIDE_WRAPPING
            ).setup_raw_qty,
            'total_lid_outside_wrappingpaper_quantity',
        )
        sheets = []
        for (__, min_qty), items in fit_qty_map.items():
            sheets.append(vo_sheet.SheetQuantity(min_qty=min_qty, items=items))
        data.update(self.env['package.sheet.quantity'].calc(self.quantity, sheets))
        return data

    def _get_init_sheet_quantity_data(self):
        return {
            'total_base_greyboard_quantity': 0,
            'total_base_inside_wrappingpaper_quantity': 0,
            'total_base_outside_wrappingpaper_quantity': 0,
            'total_lid_greyboard_quantity': 0,
            'total_lid_inside_wrappingpaper_quantity': 0,
            'total_lid_outside_wrappingpaper_quantity': 0,
        }

    def _get_price_data(self):
        self.ensure_one()
        data = {'unit_cost': 0, 'total_cost': 0}
        if self.quantity:
            cfg = self.configurator_id
            total_cost = 0
            total_cost += multiply(
                cfg.sheet_greyboard_base_id.unit_cost,
                self.total_base_greyboard_quantity,
            )
            total_cost += multiply(
                cfg.sheet_greyboard_lid_id.unit_cost, self.total_lid_greyboard_quantity
            )
            total_cost += multiply(
                cfg.sheet_wrappingpaper_base_inside_id.unit_cost,
                self.total_base_inside_wrappingpaper_quantity,
            )
            total_cost += multiply(
                cfg.sheet_wrappingpaper_base_outside_id.unit_cost,
                self.total_base_outside_wrappingpaper_quantity,
            )
            total_cost += multiply(
                cfg.sheet_wrappingpaper_lid_inside_id.unit_cost,
                self.total_lid_inside_wrappingpaper_quantity,
            )
            total_cost += multiply(
                cfg.sheet_wrappingpaper_lid_outside_id.unit_cost,
                self.total_lid_outside_wrappingpaper_quantity,
            )
            total_cost += self.total_lamination_inside_cost
            total_cost += self.total_lamination_outside_cost
            data.update(
                {'unit_cost': total_cost / self.quantity, 'total_cost': total_cost}
            )
        return data
