import base64

from footil.xtyping import bytes_to_str, str_to_bytes

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError

CACHE_DEPS = ['username', 'password']


class AuthBasic(models.Model):
    """Model to hold Basic auth records."""

    _name = "auth.basic"
    _inherit = "server.env.mixin"
    _description = "Basic Authentication"

    name = fields.Char(required=True)
    username = fields.Char()
    password = fields.Char()
    user_id = fields.Many2one(
        'res.users',
        required=True,
        help="The user used to process the requests authenticated by " "basic auth",
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Basic Authentication name must be unique.",
        )
    ]

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        auth_basic_fields = {
            'username': {},
            'password': {},
        }
        auth_basic_fields.update(base_fields)
        return auth_basic_fields

    @property
    def _raw_credentials(self):
        self.ensure_one()
        return '%s:%s' % (self.username, self.password)

    @property
    def _credentials(self):
        """Encode `username:password` pair using base64.

        Encoded byte is returned as string to allow easier comparison.
        """
        self.ensure_one()
        byte_creds = base64.b64encode(str_to_bytes(self._raw_credentials))
        return bytes_to_str(byte_creds)

    @api.model
    def _retrieve_auth_basic(self, credentials):
        return self.browse(self._retrieve_auth_basic_id(credentials))

    @api.model
    @tools.ormcache("credentials")
    def _retrieve_auth_basic_id(self, credentials):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("User is not allowed"))
        for auth_basic in self.search([]):
            if tools.consteq(credentials, auth_basic._credentials):
                return auth_basic.id
        raise ValidationError(_("The credentials %s are incorrect") % credentials)

    def _clear_key_cache(self):
        self._retrieve_auth_basic_id.clear_cache(self.env[self._name])

    @api.model
    def create(self, vals):
        """Extend to clear cache."""
        record = super().create(vals)
        self._clear_key_cache()
        return record

    def write(self, vals):
        """Extend to clear cache."""
        # NOTE. Write is not intended to be done directly. To change
        # values on existing record, unlink it and create new one!
        super().write(vals)
        if set(CACHE_DEPS).intersection(vals):
            self._clear_key_cache()
        return True

    def unlink(self):
        """Extend to clear cache."""
        res = super().unlink()
        self._clear_key_cache()
        return res
