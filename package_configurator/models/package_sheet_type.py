from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const


class PackageSheetType(models.Model):
    _name = 'package.sheet.type'
    _description = "Package Sheet Type"

    name = fields.Char(required=True)
    component_kind_ids = fields.Many2many(
        'package.component.kind',
        'package_sheet_type_component_kind_rel',
        'type_id',
        'kind_id',
    )
    thickness = fields.Float(required=True)
    # TODO: maybe should add uom.uom instead of this?..
    thickness_uom = fields.Selection(
        [("mm", "mm"), ("gsm", "gsm")],
        string="Thickness UoM",
        required=True,
        default="mm",
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    @api.depends("name", "thickness", "thickness_uom")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} {rec.thickness:2g}{rec.thickness_uom}"

    @api.constrains('thickness_uom', 'component_kind_ids')
    def _check_thickness_uom(self):
        for rec in self:
            allowed_uoms = rec._get_allowed_uoms()
            if rec.thickness_uom not in allowed_uoms:
                raise ValidationError(
                    _(
                        "%(name)s must use %(uoms)s UoM for Thickness!",
                        name=rec.name,
                        uoms=', '.join(allowed_uoms),
                    ),
                )

    def _get_allowed_uoms(self):
        self.ensure_one()
        allowed_uoms = []
        codes = self.component_kind_ids.mapped('code')
        if (
            const.ComponentKind.GREYBOARD in codes
            or const.ComponentKind.CARTON in codes
        ):
            allowed_uoms.append('mm')
        if const.ComponentKind.WRAPPINGPAPER in codes:
            allowed_uoms.append('gsm')
        return tuple(allowed_uoms)
