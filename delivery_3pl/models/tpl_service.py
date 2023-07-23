import logging

import requests
from footil.formatting import get_formatted_exception

from odoo import fields, models
from odoo.exceptions import ValidationError

from ..utils import safe_urljoin

_logger = logging.getLogger(__name__)


class TplService(models.AbstractModel):
    """Base class to be used for 3PL service models.

    When subclassing this model, it expects `auth_id` M2O field with
    comodel_name to `tpl.auth` subclass.
    """

    _name = 'tpl.service'
    _description = "3PL Service"
    _accept_header = 'application/json'

    debug = fields.Boolean()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda s: s.env.user.company_id,
    )
    # Invoice/email management fields.
    invoice_state_target = fields.Selection(
        [('draft', 'Draft'), ('open', 'Open'), ('paid', 'Paid')],
        help="If set, will create invoice to have specified state",
    )
    invoice_state_email = fields.Selection(
        [('open', 'Open'), ('paid', 'Paid')],
        help="If set, will send an email about invoice to customer. Will "
        + "send either when invoice is validated or when it is fully paid.",
    )
    journal_id = fields.Many2one(
        'account.journal',
        domain=[('type', '=', 'bank')],
        help="Bank Journal to use for payment",
    )
    warehouse_id = fields.Many2one('stock.warehouse')
    force_warehouse = fields.Boolean(
        help="Use this warehouse even if warehouse was set during initial " + "creation"
    )

    def log(self, msg, log_args=None, logger=None):
        """Log message if debug is enabled."""
        self.ensure_one()
        if not self.debug:
            return
        if not log_args:
            log_args = ()
        if logger is None:
            logger = _logger
        logger.info(msg, *log_args)

    def call_requests_method(self, method_name, endpoint, log_details='', **kwargs):
        """Call specific request method and handle response."""
        self.ensure_one()
        method = getattr(requests, method_name)
        headers = kwargs.setdefault('headers', {})
        headers['Accept'] = self._accept_header
        headers['Authorization'] = self.auth_id.prepare_auth_header()
        if log_details:
            # To make space between main log sentence.
            log_details = ' %s' % log_details
        try:
            _logger.info("Calling '%s' endpoint.%s", endpoint, log_details)
            return method(endpoint, **kwargs)
        # We raise on unexpected exceptions.
        except Exception:
            raise ValidationError(get_formatted_exception())

    def prepare_endpoint(self, path, args=None):
        """Prepare endpoint using path and extra args."""
        self.ensure_one()
        return safe_urljoin(self.auth_id.url, path, args=args)

    def get_warehouse_data(self):
        self.ensure_one()
        return (self.warehouse_id, self.force_warehouse)
