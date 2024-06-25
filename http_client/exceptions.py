from odoo.exceptions import ValidationError


class AuthError(ValidationError):
    """Exception when Authentication via auth object fails."""


class AuthDataError(ValidationError):
    """Exception when Authentication object data can't be used."""
