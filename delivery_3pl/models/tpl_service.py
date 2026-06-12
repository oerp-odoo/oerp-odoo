from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.tools.safe_eval import safe_eval

from ..value_objects import IntegrationSpec


class TplService(models.Model):
    _name = 'tpl.service'
    _description = "3PL Service"
    _order = 'sequence, id'

    @property
    def integrations(self) -> dict[str, IntegrationSpec]:
        return {}

    @property
    def integration_spec(self):
        self.ensure_one()
        return self.integrations[self.integration]

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda s: s.env.user.company_id,
    )
    sequence = fields.Integer(default=10)
    integration = fields.Selection(
        lambda s: s._get_integration_selection(),
        required=True,
    )
    http_client_profile_id = fields.Many2one('http.client.profile', copy=False)
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
    filter_expression = fields.Char(help="Use 'sale' object to match 3PL Service.")
    carrier_default_id = fields.Many2one(
        'delivery.carrier',
        string="Default Carrier",
        help="If specified, will be set on sale order confirmation for both "
        + "sale order and its related picking.",
    )

    @api.constrains('integration', 'http_client_profile_id')
    def _check_integration(self):
        for service in self:
            if (
                service.integration_spec.use_non_ok_exception
                and not service.http_client_profile_id.non_ok_exception_path
            ):
                raise ValidationError(
                    self.env._(
                        "%s integration requires HTTP Client Profile to specify "
                        + "Exception Path for Not OK Response!",
                        service.get_selection_label('integration'),
                    )
                )

    @api.constrains('filter_expression')
    def _check_filter_expression(self):
        for rec in self.filtered('filter_expression'):
            try:
                rec._match_by_filter_expression(self.env['sale.order'])
            except Exception as e:
                raise ValidationError(
                    self.env._("Incorrect Filter Expression. Got: %s", e)
                )

    def get_3pl_service(self, sale_order, integration=None, raise_not_found=True):
        services = self.search(
            self._prepare_domain(sale_order, integration=integration)
        )
        for service in services:
            if not service._match(sale_order):
                continue
            return service
        if raise_not_found:
            raise ValidationError(
                self.env._(
                    "No 3PL service found for sale order %s. Make sure"
                    + " it is created and active.",
                    sale_order.name,
                )
            )
        return self.env['tpl.service']

    def get_sale_event(self, event_name):
        self.ensure_one()
        return getattr(self.integration_spec.sale_events, event_name)

    def _get_integration_selection(self):
        return [(k, i.label) for (k, i) in self.integrations.items()]

    @api.model
    def _prepare_domain(self, sale_order, integration=None):
        domain = Domain('company_id', '=', sale_order.company_id.id)
        if integration is not None:
            domain &= Domain('integration', '=', integration)
        return domain

    def _match(self, sale_order):
        self.ensure_one()
        if not self._has_any_3pl_lines(sale_order.order_line):
            return False
        if not self.filter_expression:
            return True
        return self._match_by_filter_expression(sale_order)

    def _match_by_filter_expression(self, sale_order):
        self.ensure_one()
        return bool(
            safe_eval(self.filter_expression, self._prepare_match_context(sale_order))
        )

    @api.model
    def _prepare_match_context(self, sale_order):
        return {'sale': sale_order}

    def _has_any_3pl_lines(self, sale_lines):
        self.ensure_one()
        is_3pl_line = self.integration_spec.is_3pl_line
        return any(is_3pl_line(line) for line in sale_lines)
