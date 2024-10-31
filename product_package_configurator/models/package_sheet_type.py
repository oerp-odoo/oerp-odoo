from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const
from ..utils.misc import get_selection_label


class PackageSheetType(models.Model):
    _name = 'package.sheet.type'
    _description = "Package Sheet Type"

    name = fields.Char(required=True)
    scope = fields.Selection(const.SHEET_TYPE_SELECTION, required=True)
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

    @api.constrains('thickness_uom', 'scope')
    def _check_thickness_uom(self):
        for rec in self:
            label = get_selection_label(rec, 'scope')
            allowed_uoms = rec._get_allowed_uoms()
            if rec.thickness_uom not in allowed_uoms:
                raise ValidationError(
                    _(
                        "%(label)s must use %(uoms)s UoM for Thickness!",
                        label=label,
                        uoms=', '.join(allowed_uoms),
                    ),
                )

    def _get_allowed_uoms(self):
        self.ensure_one()
        if self.scope == const.SheetTypeScope.GREYBOARD:
            return ('mm',)
        if self.scope == const.SheetTypeScope.WRAPPINGPAPER:
            return ('gsm',)
        return ()
