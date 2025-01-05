from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const
from ..utils.search import search_default_component_kind


class PackageSheetType(models.Model):
    _name = 'package.sheet.type'
    _description = "Package Sheet Type"

    name = fields.Char(required=True)
    component_kind_id = fields.Many2one(
        'package.component.kind',
        required=True,
        default=search_default_component_kind,
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

    @api.constrains('thickness_uom', 'component_kind_id')
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
        code = self.component_kind_id.code
        if code in (const.ComponentKind.GREYBOARD, const.ComponentKind.CARTON):
            return ('mm',)
        if const.ComponentKind.WRAPPINGPAPER == code:
            return ('gsm',)
        return ()
