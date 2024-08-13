from odoo.exceptions import ValidationError


class MissingGithubError(ValidationError):
    """Exception to be raised with 404 status code."""
