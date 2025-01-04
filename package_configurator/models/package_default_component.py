from odoo import fields, models


class PackageDefaultComponent(models.Model):
    _name = 'package.default.component'
    _description = "Package Default Component"
    _rec_name = 'component_type_id'

    component_type_id = fields.Many2one(
        'package.component.type',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    _sql_constraints = [
        (
            'component_type_id_company_id_uniq',
            'unique (component_type_id, company_id)',
            'The Component Type must be unique per company!',
        )
    ]
