from odoo import fields, models


class PackageType(models.Model):
    _name = 'package.type'
    _description = "Package Type"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    component_kind_ids = fields.Many2many(
        'package.component.kind',
        'package_type_component_kind_rel',
        'type_id',
        'kind_id',
        string="Component Kinds",
    )
    component_type_ids = fields.Many2many(
        'package.component.type',
        'package_type_component_type_rel',
        'package_type_id',
        'component_type_id',
        string="Component Types",
        help="Component Types that can be used by this Package Type",
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
