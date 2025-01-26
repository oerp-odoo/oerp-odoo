from odoo import api, fields, models

from ..const import ComponentType
from ..utils.misc import compute_selection_name


class PackageComponentType(models.Model):
    _name = 'package.component.type'
    _description = "Package Component Type"

    name = fields.Char(compute='_compute_name', store=True)
    code = fields.Selection(
        [
            (ComponentType.BASE, "Base"),
            (ComponentType.LID, "Lid"),
            (ComponentType.BASE_WRAPPINGPAPER_INSIDE, "Base Inside Wrapping Paper"),
            (ComponentType.BASE_WRAPPINGPAPER_OUTSIDE, "Base Outside Wrapping Paper"),
            (ComponentType.LID_WRAPPINGPPAER_INSIDE, "Lid Inside Wrapping Paper"),
            (ComponentType.LID_WRAPPINGPPAER_OUTSIDE, "Lid Outside Wrapping Paper"),
        ],
        required=True,
    )
    component_kind_ids = fields.Many2many(
        'package.component.kind',
        'package_component_type_component_kind_rel',
        'type_id',
        'kind_id',
        string="Component Kinds",
        help="Component Kinds that are part of this Component Type",
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
