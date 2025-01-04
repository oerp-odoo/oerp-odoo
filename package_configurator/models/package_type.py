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
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
