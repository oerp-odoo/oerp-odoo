from odoo import fields, models


class PackageWrappingpaper(models.Model):

    _name = 'package.wrappingpaper'
    _inherit = 'package.sheet'
    _description = "Package Wrapping Paper"

    # TODO: should wrapping paper have thickness field like carton?
    name = fields.Char(required=True)
