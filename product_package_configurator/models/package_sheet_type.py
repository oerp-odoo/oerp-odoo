from odoo import api, fields, models

from ..const import SheetTypeScope


class PackageSheetType(models.Model):
    _name = 'package.sheet.type'
    _description = "Package Sheet Type"

    name = fields.Char(required=True)
    scope = fields.Selection(
        [
            (SheetTypeScope.GREYBOARD, "Grey Board"),
            (SheetTypeScope.WRAPPINGPAPER, "Wrapping Paper"),
        ],
        required=True,
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
