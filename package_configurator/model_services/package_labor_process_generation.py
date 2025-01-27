from collections import defaultdict

from odoo import models

from .. import const
from ..utils.component import get_comps
from ..value_objects import labor as vo_labor


def get_comp_type(components_data: list[tuple[const.ComponentType, int]]):
    for (comp_type, cnt) in components_data:
        for __ in range(cnt):
            yield comp_type


class PackageLaborProcessGeneration(models.AbstractModel):
    _name = 'package.labor.process.generation'
    _description = "Package Labor Process Generation"

    def generate(
        self, labor_rec, cfg, component_types: tuple[const.ComponentType] = ()
    ):
        processes = []
        for item in labor_rec.item_ids:
            processes.extend(self._generate(item, cfg, component_types=component_types))
        return processes

    def _generate(
        self, labor_item, cfg, component_types: tuple[const.ComponentType] = ()
    ):
        labor_type_code = labor_item.labor_type_id.code
        method_name = f'_prepare_cdata_for_{labor_type_code}_process'
        components_data = getattr(self, method_name)(labor_item, cfg)
        if component_types:
            components_data = [cd for cd in components_data if cd[0] in component_types]
        processes = []
        for comp_type in get_comp_type(components_data):
            processes.append(
                vo_labor.LaborProcess.from_labor_item(
                    labor_item, component_type=comp_type
                )
            )
        return processes

    def _prepare_cdata_for_generic_process(self, labor_item, cfg):
        # Generic processes are valid only for base and lid components!
        codes = self._filter_component_type_codes(cfg, {'base', 'lid'})
        # Generic processes are used for each component only once!
        return [(code, 1) for code in codes]

    def _prepare_cdata_for_lamination_process(self, labor_item, cfg):
        sides = set(cfg.cfg_lamination_ids.mapped('side'))
        if not sides:
            return []
        comp_type_codes = []
        for side in sides:
            comp_type_codes.extend(
                [f'base_wrappingpaper_{side}', f'lid_wrappingpaper_{side}']
            )
        comps = get_comps(cfg.component_ids, *comp_type_codes, keep_empty=False)
        # Lamination process is used for each component only once!
        return [(comp.component_type_id.code, 1) for comp in comps]

    def _prepare_cdata_for_wrappingpaper_cladding_process(self, labor_item, cfg):
        codes = self._filter_component_type_codes(
            cfg,
            {
                'base_wrappingpaper_inside',
                'base_wrappingpaper_outside',
                'lid_wrappingpaper_inside',
                'lid_wrappingpaper_outside',
            },
        )
        # WP cladding process is used for each component only once!
        return [(code, 1) for code in codes]

    def _prepare_cdata_for_foiling_process(self, labor_item, cfg):
        data = defaultdict(int)
        for cfg_foil in cfg.cfg_foil_ids:
            data[cfg_foil.component_id.component_type_id.code] += 1
        # Foiling process can be used multiple times on single component!
        return [(k, v) for k, v in data.items()]

    def _prepare_cdata_for_insert_putting_process(self, labor_item, cfg):
        inserts = cfg.configurator_insert_ids
        if not inserts:
            return []
        # We tie inserts putting process with base component.
        return [('base', len(inserts))]

    def _prepare_cdata_for_insert_formation_process(self, labor_item, cfg):
        # We use formation process for insert package type only!
        if cfg.package_type_id.code != const.PackageType.INSERT:
            return []
        # For inserts, formation process is assumed to always be needed!
        return [('base', 1)]

    def _filter_component_type_codes(self, cfg, component_type_codes: set):
        return (
            set(cfg.component_ids.mapped('component_type_id.code'))
            & component_type_codes
        )
