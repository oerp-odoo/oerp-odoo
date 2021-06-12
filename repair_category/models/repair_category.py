from odoo import models, fields


class RepairCategory(models.Model):
    """Model to classify different type of repair orders."""

    _name = 'repair.category'
    _description = "Repair Category"

    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one('res.company')
