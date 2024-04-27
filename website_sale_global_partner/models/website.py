from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    is_global_partner = fields.Boolean(
        help="Will not set company_id when creating partner"
    )
