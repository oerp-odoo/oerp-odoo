from odoo import models


class GithubAuth(models.Model):
    """Authentication model for github requests."""

    _name = 'github.auth'
    _inherit = 'http.client.auth'
    _description = "Github Client Authentication"
