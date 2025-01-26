from odoo import api, fields, models

from ..const import ComponentKind
from ..utils.misc import compute_selection_name


class PackageComponentKind(models.Model):
    _name = 'package.component.kind'
    _description = "Package Component Kind"

    name = fields.Char(compute='_compute_name', store=True)
    code = fields.Selection(
        [
            (ComponentKind.GREYBOARD, "Grey Board"),
            (ComponentKind.CARTON, "Carton"),
            (ComponentKind.WRAPPINGPAPER, "Wrapping Paper"),
        ],
        required=True,
    )

    @api.depends('code')
    def _compute_name(self):
        compute_selection_name(self, 'code')

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
