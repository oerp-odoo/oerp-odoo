from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.odootil.tools.parsing import parse_positive_int_list, parse_to_list
from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import const


class HttpClientRetry(models.Model):
    """Model to manage requests retry strategies."""

    _name = 'http.client.retry'
    _description = "HTTP Client Retry"

    name = fields.Char(required=True)
    mount_prefixes = fields.Char(
        required=True,
        default=const.DEFAULT_RETRY_MOUNT_PFX,
        help="Comma separated list of session mount prefixes to use retry on.",
    )
    retries_total = fields.Integer(
        string="Total Retries",
        help="Total number of retries to allow. Takes precedence over other counts. "
        + "Set to 0 to fail on the first retry. Set -1 to disable this.",
        default=const.DEFAULT_TOTAL_RETRY,
    )
    retries_connect = fields.Integer(
        string="Connect Retries",
        help="How many connection-related errors to retry on. Set -1 to disable this.",
        default=-1,
    )
    retries_read = fields.Integer(
        string="Read Retries",
        help="How many times to retry on read errors. Set -1 to disable this.",
        default=-1,
    )
    retries_redirect = fields.Integer(
        string="Redirect Retries",
        help="How many redirects to perform. Limit this to avoid infinite redirect",
        default=-1,
    )
    backoff_factor = fields.Float(
        help="A backoff factor to apply between attempts after the second try: "
        + "{backoff factor} * (2 ** ({number of total retries} - 1))"
    )
    allowed_methods = fields.Char(
        help="Comma separated list of uppercased HTTP method verbs that we should "
        + "retry on"
    )
    status_forcelist = fields.Char(
        help="A comma separated, list of integer HTTP status codes that we should"
        + " force a retry on."
    )
    raise_on_status = fields.Boolean(
        help="Whether we should raise an exception, or return a response, "
        + "if status falls in ``status_forcelist`` range and retries have "
        + "been exhausted.",
        default=True,
    )
    raise_on_redirect = fields.Boolean(
        help="Whether, if the number of redirects is exhausted, to raise a "
        + "MaxRetryError, or to return a response with a response code in the 3xx"
        + " range.",
        default=True,
    )

    @api.constrains('allowed_methods')
    def _check_allowed_methods(self):
        for rec in self:
            if not rec.allowed_methods:
                continue
            if rec.allowed_methods != rec.allowed_methods.upper():
                raise ValidationError(_("Allowed Methods must be uppercased!"))
            methods = parse_to_list(rec.allowed_methods, clean_whitespace=True)
            valid_methods = list(HttpVerb)
            for method in methods:
                if method not in valid_methods:
                    raise ValidationError(
                        _(
                            "Incorrect allowed method (%(method)s) used. Valid"
                            + " methods: %(methods)s",
                            method=method,
                            methods=', '.join(valid_methods),
                        )
                    )

    @api.constrains('status_forcelist')
    def _check_status_forcelist(self):
        for rec in self:
            if not rec.status_forcelist:
                continue
            try:
                parse_positive_int_list(rec.status_forcelist)
            except Exception:
                raise ValidationError(
                    _("Status Forcelist must be positive comma separated integers")
                )
