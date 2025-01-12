from odoo import fields, models

from ..const import ComponentType


class PackageComponentType(models.Model):
    _name = 'package.component.type'
    _description = "Package Component Type"

    name = fields.Char(required=True)
    code = fields.Selection(
        [
            (ComponentType.BASE, "Base"),
            (ComponentType.LID, "Lid"),
            (ComponentType.BASE_WRAPPINGPAPER_INSIDE, "Base Wrappingpaper Inside"),
            (ComponentType.BASE_WRAPPINGPAPER_OUTSIDE, "Base Wrappingpaper Outside"),
            (ComponentType.LID_WRAPPINGPPAER_INSIDE, "Lid Wrappingppaer Inside"),
            (ComponentType.LID_WRAPPINGPPAER_OUTSIDE, "Lid Wrappingppaer Outside"),
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

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
