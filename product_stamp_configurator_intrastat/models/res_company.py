from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    intrastat_stamp_default_code_id = fields.Many2one(
        'account.intrastat.code',
        string='Default Stamp Commodity Code',
    )
