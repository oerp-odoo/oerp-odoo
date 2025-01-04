from odoo import fields, models


class PackageComponentKind(models.Model):
    _name = 'package.component.kind'
    _description = "Package Component Kind"

    name = fields.Char(required=True)
    code = fields.Char(required=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
