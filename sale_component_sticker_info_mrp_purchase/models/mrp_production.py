from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_group_name = fields.Char(readonly=True, copy=False)
