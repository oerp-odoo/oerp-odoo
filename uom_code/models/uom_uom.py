from odoo import fields, models


class UomUom(models.Model):
    """Extend to code field."""

    _inherit = 'uom.uom'

    code = fields.Char()

    _sql_constraints = [('code_uniq', 'unique (code)', 'The Code must be unique!')]
