from odoo import fields, models


class BaseDataLabel(models.Model):
    _name = 'base.data.label'
    _description = "Base Data Label"

    name = fields.Char(required=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name)',
            'The name must be unique !',
        )
    ]
