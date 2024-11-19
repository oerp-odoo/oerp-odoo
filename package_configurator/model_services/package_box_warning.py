from odoo import models

from ..utils.misc import get_selection_label
from ..value_objects import package_warning as vo_pw


class PackageBoxWarning(models.AbstractModel):
    _name = 'package.box.warning'
    _description = "Package Box Warning Service"

    def get_warnings(self, cfg) -> list[vo_pw.PackageWarning]:
        res = []
        res.extend(self._get_warnings_component_not_fit_sheet(cfg))
        wrn = self.get_warning_missing_default_components(cfg)
        if wrn is not None:
            res.append(wrn)
        return res

    def _get_warnings_component_not_fit_sheet(self, cfg) -> list[vo_pw.PackageWarning]:
        res = []
        for comp in cfg.component_ids:
            if (
                not comp.component_length
                or not comp.component_width
                or not comp.sheet_id
            ):
                continue
            # TODO: maybe we should fit all this in single warning?..
            if not comp.fit_qty:
                label = get_selection_label(comp, 'component_type')
                sheet_name = comp.sheet_id.display_name
                res.append(
                    vo_pw.PackageWarning(
                        warning_type=vo_pw.WarningType.DANGER,
                        message=(
                            f'Component "{label}" won\'t fit on sheet {sheet_name}'
                        ),
                    )
                )
        return res

    def get_warning_missing_default_components(self, cfg):
        default_comps = cfg.box_type_id.default_component_ids
        if not default_comps:
            return None
        default_comp_types = set(default_comps.mapped('component_type'))
        current_comp_types = set(cfg.component_ids.mapped('component_type'))
        missing = default_comp_types - current_comp_types
        if not missing:
            return None
        missing_comps = default_comps.filtered(lambda r: r.component_type in missing)
        labels = ', '.join(
            [
                f"<strong>{get_selection_label(mc, 'component_type')}</strong>"
                for mc in missing_comps
            ]
        )
        return vo_pw.PackageWarning(
            warning_type=vo_pw.WarningType.WARNING,
            message=f'Expected default components not used: {labels}',
        )
