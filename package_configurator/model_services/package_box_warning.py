from odoo import models

from ..utils.misc import get_selection_label
from ..value_objects import package_warning as vo_pw


class PackageBoxWarning(models.AbstractModel):
    _name = 'package.box.warning'
    _description = "Package Box Warning Service"

    def get_warnings(self, cfg) -> list[vo_pw.PackageWarning]:
        res = []
        # Don't check for warning if base measurements are not set yet.
        if not cfg.base_length or not cfg.base_width or not cfg.base_height:
            return res
        res.extend(self._get_warnings_component_not_fit_sheet(cfg))
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
