from odoo import api, models


class HttpClientAuth(models.AbstractModel):
    """Extend to integrate with server_environment."""

    _name = 'http.client.auth'
    _inherit = ['server.env.mixin', 'http.client.auth']

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        # TODO: might be worth adding other fields, to make configuration
        # more flexible.
        http_client_fields = {
            'url': {},
            'identifier': {},
            'secret': {},
            'path_auth': {},
            'path_refresh': {},
            'path_verify': {},
        }
        http_client_fields.update(base_fields)
        return http_client_fields

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self.handle_name(vals)
        return super().create(vals)

    def write(self, vals):
        self.handle_name(vals)
        return super().write(vals)

    @api.model
    def handle_name(self, vals):
        if vals.get('name'):
            vals['name'] = self.env['server.env.techname.mixin']._normalize_tech_name(
                vals['name']
            )
