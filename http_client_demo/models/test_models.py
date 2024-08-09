from odoo import api, models

GROUP_CONTROLLER_XMLID = 'http_client_demo.controller_group_use'


class HttpClientTestAuth(models.Model):
    """Model to handle test auth."""

    _name = 'http.client.test.auth'
    _inherit = 'http.client.auth'
    _description = "HTTP Client Test Authentication"


class HttpClientTestController(models.AbstractModel):
    """Test controller model."""

    _name = 'http.client.test.controller'
    _inherit = 'http.client.controller'
    _description = "HTTP Client Controller"
    _auth_model = 'http.client.test.auth'

    @api.model
    def is_controller_enabled(self):
        """Override to implement enabler."""
        group_user = self.env.ref('base.group_user')
        group_controller = self.env.ref(GROUP_CONTROLLER_XMLID)
        return group_controller in group_user.implied_ids
