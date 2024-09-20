from odoo import fields, models


class PackageCarton(models.Model):

    _name = 'package.carton'
    _inherit = 'package.sheet'
    _description = "Package Carton"

    name = fields.Char(required=True)
    thickness = fields.Float("Thickness, mm", required=True)
