from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    orderpoint_no_to_date = fields.Boolean("Ignore Scheduled Date for Reordering Rules")
