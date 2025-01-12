from odoo import fields, models

from ..const import ComponentKind


class PackageComponentKind(models.Model):
    _name = 'package.component.kind'
    _description = "Package Component Kind"

    name = fields.Char(required=True)
    code = fields.Selection(
        [
            (ComponentKind.GREYBOARD, "Greyboard"),
            (ComponentKind.CARTON, "Carton"),
            (ComponentKind.WRAPPINGPAPER, "Wrappingpaper"),
        ],
        required=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
