from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    auto_plan = fields.Boolean(
        copy=False, help="Automatically plan Manufacturing Order once it is created"
    )
