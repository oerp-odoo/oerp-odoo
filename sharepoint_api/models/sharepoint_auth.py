from odoo import models


class SharepointAuth(models.Model):
    """Authentication model for sharepoint requests."""

    _name = 'sharepoint.auth'
    _inherit = 'http.client.auth'
    _description = "Sharepoint Client Authentication"
