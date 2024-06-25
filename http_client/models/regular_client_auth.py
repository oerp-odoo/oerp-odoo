from odoo import fields, models


class RegularClientAuth(models.Model):
    """Regular Auth implementation for general use cases."""

    _name = 'regular.client.auth'
    _inherit = 'http.client.auth'
    _description = "Regular Client Authentication"

    # Used to conveniently separate auth records depending on their
    # use cases.
    use_case = fields.Selection([])
