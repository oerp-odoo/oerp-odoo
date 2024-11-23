from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_grouping = fields.Selection(
        [
            ('no_grouping', "No Grouping"),
            ('root_procure_group', "By Root Procurement Group"),
        ],
        "Grouping for Purchases",
    )
