import base64
import validators

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TplAuth(models.AbstractModel):
    """Base auth model to handle 3PL authentication.

    Make sure this model subclass is accessible only to admin type
    users!
    """

    _name = 'tpl.auth'
    _description = "3PL Authentication"

    name = fields.Char(required=True)
    url = fields.Char(string="URL", required=True)
    key = fields.Char(string="API Key", required=True)
    secret = fields.Char(required=True)

    @api.constrains('url')
    def _check_url(self):
        """Check URL validity."""
        for auth in self:
            if not validators.url(auth.url or ''):
                raise ValidationError(_("'%s' is not valid URL.", auth.url))

    def prepare_auth_header(self):
        """Override to implement different authentication."""
        self.ensure_one()
        val = f'{self.key}:{self.secret}'.encode()
        return f'Basic {base64.b64encode(val).decode()}'
