from odoo import fields, models


class HttpClientProfile(models.Model):
    _inherit = 'http.client.profile'

    integration = fields.Selection(
        selection_add=[('my_integration_1', 'My Integration 1')],
        ondelete={'my_integration_1': 'cascade'},
    )
