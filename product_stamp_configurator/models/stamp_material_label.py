from odoo import fields, models


class StampMaterialLabel(models.Model):
    _name = 'stamp.material.label'
    _description = "Stamp Material Label"

    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name)',
            'The name must be unique !',
        )
    ]
