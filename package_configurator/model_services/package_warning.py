from odoo import models

from ..value_objects import package_warning as vo_pw


class PackageWarning(models.AbstractModel):
    _name = 'package.warning'
    _description = "Package Warning Service"

    def get_formatted_warnings(self, cfg) -> str | bool:
        warnings = self.get_warnings(cfg)
        if not warnings:
            return False
        return self._format_description_warnings(warnings)

    def get_warnings(self, cfg) -> list[vo_pw.PackageWarning]:
        res = []
        res.extend(self._get_warnings_component_not_fit_sheet(cfg))
        wrn = self._get_warning_missing_default_components(cfg)
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
                sheet_name = comp.sheet_id.display_name
                res.append(
                    vo_pw.PackageWarning(
                        warning_type=vo_pw.WarningType.DANGER,
                        message=(
                            f'Component "{comp.display_name}" won\'t fit on sheet'
                            + f" {sheet_name}"
                        ),
                    )
                )
        return res

    def _get_warning_missing_default_components(self, cfg):
        default_comps = cfg.package_kind_id.default_component_ids
        if not default_comps:
            return None
        default_comp_types = set(default_comps.mapped('component_type_id.code'))
        current_comp_types = set(cfg.component_ids.mapped('component_type_id.code'))
        missing = default_comp_types - current_comp_types
        if not missing:
            return None
        missing_comps = default_comps.filtered(
            lambda r: r.component_type_id.code in missing
        )
        labels = ', '.join(
            [f"<strong>{mc.display_name}</strong>" for mc in missing_comps]
        )
        return vo_pw.PackageWarning(
            warning_type=vo_pw.WarningType.WARNING,
            message=f'Expected default components not used: {labels}',
        )

    def _format_description_warnings(self, warnings: list[vo_pw.PackageWarning]):
        li_items = []
        for warning in warnings:
            klass = f'list-group-item list-group-item-{warning.warning_type.value}'
            li_items.append(f'<li class="{klass}">{warning.message}</li>')
        li_str = '\n'.join(li_items)
        return f'<ul class="list-group">{li_str}</ul>'
