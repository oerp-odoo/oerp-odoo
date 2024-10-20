from odoo import api, fields, models

from .. import const
from ..utils.fitter import calc_sheet_quantity
from ..value_objects.layout import Layout2D

MAP_PART_FIT_QTY = {
    const.CirculationSetupPart.BASE_CARTON: 'base_layout_fit_qty',
    const.CirculationSetupPart.LID_CARTON: 'lid_layout_fit_qty',
    const.CirculationSetupPart.BASE_INSIDE_WRAPPING: 'base_inside_fit_qty',
    const.CirculationSetupPart.BASE_OUTSIDE_WRAPPING: 'base_outside_fit_qty',
    const.CirculationSetupPart.LID_INSIDE_WRAPPING: 'lid_inside_fit_qty',
    const.CirculationSetupPart.LID_OUTSIDE_WRAPPING: 'lid_outside_fit_qty',
}


class PackageConfiguratorBoxCirculationSetup(models.Model):
    _name = 'package.configurator.box.circulation.setup'
    _description = "Package Configurator Box Circulation Setup"

    circulation_id = fields.Many2one(
        'package.configurator.box.circulation',
        required=True,
    )
    part = fields.Selection(
        [
            (const.CirculationSetupPart.BASE_CARTON, "Base Carton"),
            (const.CirculationSetupPart.LID_CARTON, "Lid Carton"),
            (const.CirculationSetupPart.BASE_INSIDE_WRAPPING, "Base Inside Wrapping"),
            (const.CirculationSetupPart.BASE_OUTSIDE_WRAPPING, "Base Outside Wrapping"),
            (const.CirculationSetupPart.LID_INSIDE_WRAPPING, "Lid Inside Wrapping"),
            (const.CirculationSetupPart.LID_OUTSIDE_WRAPPING, "Lid Outside Wrapping"),
        ],
        required=True,
    )
    setup_rule_id = fields.Many2one('package.box.setup.rule', required=True)
    setup_id = fields.Many2one(related='setup_rule_id.setup_id')
    setup_raw_qty = fields.Integer(
        "Raw Setup Quantity", compute='_compute_setup_raw_qty'
    )

    @api.depends(
        'circulation_id.configurator_id.base_layout_fit_qty',
        'circulation_id.configurator_id.base_inside_fit_qty',
        'circulation_id.configurator_id.base_outside_fit_qty',
        'circulation_id.configurator_id.lid_layout_fit_qty',
        'circulation_id.configurator_id.lid_inside_fit_qty',
        'circulation_id.configurator_id.lid_outside_fit_qty',
        'setup_rule_id',
    )
    def _compute_setup_raw_qty(self):
        for rec in self:
            cfg = rec.circulation_id.configurator_id
            setup_raw_qty = 0
            fit_qty = cfg[MAP_PART_FIT_QTY[rec.part]]
            if fit_qty:
                setup_raw_qty = calc_sheet_quantity(
                    rec.setup_rule_id.setup_qty, fit_qty
                )
            rec.setup_raw_qty = setup_raw_qty

    @api.model
    def prepare_circulation_setups(self, circulation, setups):
        vals_list = []
        box_type = circulation.configurator_id.box_type_id
        for part, layout in self._prepare_circulation_setup_part_layouts(circulation):
            setup_rule = setups.match_setup_rule(
                circulation.quantity, layout=layout, box_type=box_type
            )
            if not setup_rule:
                continue
            vals_list.append(
                self._prepare_circulation_setup(part, circulation, setup_rule)
            )
        return vals_list

    @api.model
    def _prepare_circulation_setup(self, part, circulation, setup_rule):
        return {
            'part': part,
            'circulation_id': circulation.id,
            'setup_rule_id': setup_rule.id,
        }

    @api.model
    def _prepare_circulation_setup_part_layouts(
        self, circulation
    ) -> list[tuple[const.CirculationSetupPart, Layout2D]]:
        cfg = circulation.configurator_id
        # NOTE. For now assuming that base/lid carton parts are always used!
        res = [
            (
                const.CirculationSetupPart.BASE_CARTON,
                Layout2D(length=cfg.base_layout_length, width=cfg.base_layout_width),
            ),
            (
                const.CirculationSetupPart.LID_CARTON,
                Layout2D(length=cfg.base_layout_length, width=cfg.base_layout_width),
            ),
        ]
        if cfg.wrappingpaper_base_inside_id:
            res.append(
                (
                    const.CirculationSetupPart.BASE_INSIDE_WRAPPING,
                    Layout2D(
                        length=cfg.base_inside_wrapping_length,
                        width=cfg.base_inside_wrapping_width,
                    ),
                )
            )
        if cfg.wrappingpaper_base_outside_id:
            res.append(
                (
                    const.CirculationSetupPart.BASE_OUTSIDE_WRAPPING,
                    Layout2D(
                        length=cfg.base_outside_wrapping_length,
                        width=cfg.base_outside_wrapping_width,
                    ),
                )
            )
        if cfg.wrappingpaper_lid_inside_id:
            res.append(
                (
                    const.CirculationSetupPart.LID_INSIDE_WRAPPING,
                    Layout2D(
                        length=cfg.lid_inside_wrapping_length,
                        width=cfg.lid_inside_wrapping_width,
                    ),
                )
            )
        if cfg.wrappingpaper_lid_outside_id:
            res.append(
                (
                    const.CirculationSetupPart.LID_OUTSIDE_WRAPPING,
                    Layout2D(
                        length=cfg.lid_outside_wrapping_length,
                        width=cfg.lid_outside_wrapping_width,
                    ),
                )
            )
        return res
