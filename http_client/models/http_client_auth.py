import base64

import requests

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const
from ..exceptions import AuthDataError, AuthError
from ..utils import build_url, check_url, is_jwt_token_expired
from ..value_objects.request import RelativePath

TOKEN_AUTH_PREFIX_MAP = {'bearer': 'Bearer', 'jwt': 'JWT'}


def _prepare_payload(content_type, data):
    if content_type == 'json':
        return {'json': data}
    # x-www-form-urlencoded type.
    return {'data': data}


class HttpClientAuth(models.Model):
    """Base Authentication model to connect with HTTP calls."""

    _name = 'http.client.auth'
    _description = "HTTP Client Authentication"

    name = fields.Char(copy=False)
    base_url = fields.Char("Base URL", help="Base URL for authentication")
    auth_method = fields.Selection(
        [
            ('none', "None"),
            ('basic', "Basic"),
            ('bearer', "Bearer"),
            ('jwt', 'JWT'),
            ('api_key', "API Key"),
        ],
        required=True,
        default='none',
        copy=False,
    )
    identifier = fields.Char(copy=False)
    secret = fields.Char(copy=False)
    access_token = fields.Char(copy=False)
    refresh_token = fields.Char(copy=False)
    token_expire_delta = fields.Integer(
        default=const.DEFAULT_EXPIRE_DELTA,
        help="Delta to use when comparing token expiration. E.g -60, means"
        + " renew token even if it would still be valid for 60 seconds."
        + "Set 0 to compare with exact expiration time.",
    )
    # Part of RFC 6749 standard.
    grant_type = fields.Selection(
        [
            ('client_credentials', 'Client Credentials'),
            ('password', 'Password'),
        ]
    )
    # For request
    content_type = fields.Selection(
        [
            ('x-www-form-urlencoded', "X WWW Form Urlencoded"),
            ('json', "JSON"),
        ],
        default='x-www-form-urlencoded',
    )
    scope = fields.Char()
    path_auth = fields.Char("Authentication Path")
    path_refresh = fields.Char(
        "Token Refresh Path",
        help="If set, will try to refresh access token with refresh token "
        + "when it is expired.",
    )
    path_verify = fields.Char(
        "Token Verify Path",
        help="If set, will be able to verify existing access token validity",
    )
    company_id = fields.Many2one('res.company', default=lambda s: s.env.user.company_id)
    state = fields.Selection(
        [('draft', "Not Confirmed"), ('confirmed', "Confirmed")],
        default='draft',
        copy=False,
        readonly=True,
        required=True,
    )

    _name_uniq = models.Constraint('unique (name)', "The name must be unique!")

    @property
    def _auth_endpoint(self):
        """Return endpoint for authentication."""
        return self._form_custom_endpoint('auth')

    @property
    def _refresh_endpoint(self):
        """Return endpoint for refreshing token."""
        return self._form_custom_endpoint('refresh')

    @property
    def _verify_endpoint(self):
        return self._form_custom_endpoint('verify')

    @api.onchange('auth_method')
    def _onchange_auth_method(self):
        if self.auth_method == 'none':
            self.grant_type = False
        if self.auth_method == 'api_key' and not self.identifier:
            self.identifier = const.DEFAULT_API_KEY_HEADER

    @api.constrains('base_url')
    def _check_base_url(self):
        for rec in self.filtered('base_url'):
            check_url(self.env, rec.base_url)

    @api.constrains('token_expire_delta')
    def _check_token_expire_delta(self):
        for rec in self:
            if rec.token_expire_delta > 0:
                raise ValidationError(_("Token Expire Delta must be 0 or lower!"))

    def provide_token(self, force_new=False):
        """Return either saved token or generate new one if needed."""
        self.ensure_one()
        if self.grant_type:
            if self.path_refresh:
                return self._handle_token_with_refresh(force_new=force_new)
            return self._handle_token_without_refresh(force_new=force_new)
        # Using fixed value if no token generation was specified.
        return self.secret

    def authorize(self):
        """Return authorization headers.

        Can also refresh secrets in case temporary secrets are used
        (like in access/refresh tokens case).
        """
        self.ensure_one()
        self._validate_auth_data()
        auth_method = self.auth_method
        if auth_method == 'basic':
            return {'Authorization': self._prepare_basic_auth()}
        elif auth_method == 'api_key':
            return {self.identifier: self.secret}
        elif auth_method in TOKEN_AUTH_PREFIX_MAP:
            prefix = TOKEN_AUTH_PREFIX_MAP[auth_method]
            return {'Authorization': f'{prefix} {self.provide_token()}'}
        return {}

    def name_get(self):
        return [(r.id, r.name or f'({r.id}) {r.url}') for r in self]

    def action_confirm(self):
        """Confirm Authentication records to be used."""
        self.write({'state': 'confirmed'})

    def action_to_draft(self):
        """Set Authentication records back to draft state."""
        self.write({'state': 'draft'})

    def action_login(self):
        """Login to remote system and save new token for a session."""
        self.ensure_one()
        self.provide_token(force_new=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Login was Successful!"),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_verify(self):
        """Verify current session is still valid."""
        self.ensure_one()
        if not self.access_token:
            raise ValidationError(_("There is no Session to verify!"))
        self._verify_token()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Session is Valid!"),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_logout(self):
        """Remove session (tokens) from auth."""
        self.ensure_one()
        self.write(
            {
                'access_token': False,
                'refresh_token': False,
            }
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Logout was Successful!"),
                'type': 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _form_custom_endpoint(self, name):
        self.ensure_one()
        path_fname = f'path_{name}'
        path = self[path_fname]
        return build_url(self.base_url, RelativePath(pattern=path))

    @api.model
    def _get_domain(self, company_id=False):
        return [('state', '=', 'confirmed'), ('company_id', '=', company_id)]

    def _prepare_basic_auth(self):
        self.ensure_one()
        v = f'{self.identifier}:{self.secret}'
        secret = base64.b64encode(v.encode()).decode()
        return f'Basic {secret}'

    def _validate_auth_data(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise AuthDataError(
                _("Authentication data can only be used if it is confirmed!")
            )

    def _handle_token_with_refresh(self, force_new=False):
        self.ensure_one()
        # We get new tokens either if this is initial call (no tokens
        # at all) or both tokens are expired, so we need new ones.
        if (
            force_new
            or not self.access_token
            or not self.refresh_token
            or (
                self._is_jwt_token_expired(self.access_token)
                and self._is_jwt_token_expired(self.refresh_token)
            )
        ):
            token_data = self._request_new_token()
            # Save it for later use.
            self.write(
                {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                }
            )
            return token_data['access_token']
        access_token = self.access_token
        if self._is_jwt_token_expired(access_token):
            try:
                data = self._request_refresh_token()
            except AuthError:
                # If we can't refresh access token, it might mean that
                # refresh token itself was blacklisted, so we try to
                # re-login (save new session of tokens).
                return self._handle_token_with_refresh(force_new=True)
            access_token = data['access']
            vals = {'access_token': access_token}
            # If it returns refresh token, we rotate it, because
            # it means refresh token can be used only once!
            if data.get('refresh'):
                vals['refresh_token'] = data['refresh']
            self.write(vals)
        return access_token

    def _handle_token_without_refresh(self, force_new=False):
        self.ensure_one()
        # We get new token either if this is initial call (no token
        # at all) or token is expired.
        if (
            force_new
            or not self.access_token
            or self._is_jwt_token_expired(self.access_token)
        ):
            token_data = self._request_new_token()
            # Save it for later use.
            self.access_token = token_data['access_token']
            return token_data['access_token']
        return self.access_token

    def _prepare_common_payload_data(self):
        self.ensure_one()
        data = {
            'grant_type': self.grant_type,
        }
        if self.scope:
            data['scope'] = self.scope
        return data

    def _prepare_client_credentials_payload(self):
        self.ensure_one()
        data = self._prepare_common_payload_data()
        data.update(
            {
                'client_id': self.identifier,
                'client_secret': self.secret,
            }
        )
        return data

    def _prepare_password_payload(self):
        self.ensure_one()
        data = self._prepare_common_payload_data()
        data.update(
            {
                'username': self.identifier,
                'password': self.secret,
            }
        )
        return data

    def _request_new_token(self):
        """Use specific grant type to get new token."""
        self.ensure_one()
        data = getattr(self, '_prepare_%s_payload' % self.grant_type)()
        return self._do_auth_request(self._auth_endpoint, data)

    def _verify_token(self):
        self.ensure_one()
        # NOTE. Other implementations might not follow same format! If
        # we would encounter other format, will need to abstract this
        # part!
        data = {'token': self.access_token}
        return self._do_auth_request(self._verify_endpoint, data)

    def _request_refresh_token(self):
        """Use refresh token to get new access token."""
        self.ensure_one()
        # NOTE. Other implementations might not follow same format! If
        # we would encounter other format, will need to abstract this
        # part!
        data = {'refresh': self.refresh_token}
        return self._do_auth_request(self._refresh_endpoint, data)

    def _do_auth_request(self, endpoint, data):
        self.ensure_one()
        # TODO: make timeout configurable instead of not specifying
        # any timeout at all!
        response = requests.post(  # pylint: disable=E8106 # nosec B113
            endpoint,
            **_prepare_payload(self.content_type, data),
        )
        if not response.ok:
            self.env['http.client'].raise_response_error(response, AuthError)
        return response.json()

    def _is_jwt_token_expired(self, token):
        self.ensure_one()
        return is_jwt_token_expired(token, delta=self.token_expire_delta)
