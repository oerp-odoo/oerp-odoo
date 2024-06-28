from odoo.exceptions import ValidationError


class MissingSharepointError(ValidationError):
    """Exception to be raised with 404 status code."""
