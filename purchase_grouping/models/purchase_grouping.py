from odoo import fields, models


class PurchaseGrouping(models.Model):
    _name = 'purchase.grouping'
    _description = "Purchase Grouping"

    name = fields.Char(required=True)
    code = fields.Char(required=True)

    _sql_constraints = [
        (
            'name_uniq',
            'unique (name)',
            'The Name must be unique !',
        ),
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        ),
    ]
