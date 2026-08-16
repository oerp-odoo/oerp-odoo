import ast
import logging
from datetime import datetime, timedelta

from footil.formatting import get_formatted_exception

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

DEFAULT_DAYS = 120
DEFAULT_DATE_UPDATED_XMLID = 'sale.field_sale_order__write_date'
AUTOVACUUM_STATES = ('draft', 'sent')


_logger = logging.getLogger(__name__)


class SaleAutovacuumRule(models.Model):
    """Model to specify when old sale orders should be cleaned up."""

    _name = 'sale.autovacuum.rule'
    _inherit = 'mail.thread'
    _description = "Sale Autovacuum Rule"
    _order = 'sequence, id'

    name = fields.Char(required=True)
    state = fields.Selection(
        [
            ('draft', "Draft"),
            ('in_progress', "In Progress"),
        ],
        required=True,
        copy=False,
        default='draft',
    )
    days = fields.Integer(
        "Days Last Updated",
        help="Filter to only include sale orders that were last updated "
        + "some days ago",
        default=DEFAULT_DAYS,
    )
    field_date_updated_id = fields.Many2one(
        'ir.model.fields',
        required=True,
        domain=[
            ('ttype', '=', 'datetime'),
            ('model_id.model', '=', 'sale.order'),
        ],
        default=lambda s: s.env.ref(DEFAULT_DATE_UPDATED_XMLID),
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    action = fields.Selection(
        [('cancel', "Cancel"), ('unlink', "Delete")],
        default='cancel',
        required=True,
    )
    domain = fields.Char(default="[]", required=True)
    final_domain = fields.Char(compute='_compute_final_domain')

    def _compute_final_domain(self):
        for rule in self:
            rule.final_domain = str(rule._prepare_final_domain())

    @api.constrains('days')
    def _check_days(self):
        for rule in self:
            if rule.days < 1:
                raise ValidationError(
                    self.env._("Days Last Updated must be greater than 0!")
                )

    @api.constrains('domain')
    def _check_domain(self):
        for rule in self:
            try:
                domain = Domain(ast.literal_eval(rule.domain))
                self.env['sale.order'].search_count(domain)
            except (ValueError, AssertionError, TypeError) as e:
                raise ValidationError(
                    self.env._(
                        "Incorrect domain: %(domain)s. Error: %(err)s",
                        domain=rule.domain,
                        err=e,
                    )
                )

    def action_confirm(self):
        self.write({'state': 'in_progress'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_autovacuum(self, limit=None):
        self.ensure_one()
        self._validate_autovacuum()
        sales = self.find_sale_orders(limit=limit)
        if sales:
            action_method = getattr(self, f'_action_autovacuum_{self.action}')
            action_method(sales)
        return True

    @api.model
    def process(self, auto_commit=False, limit=None, rule_ids=None):
        """Process multiple autovacuum rules.

        Intended to be run by cron job.
        """
        domain = [('state', '=', 'in_progress')]
        if rule_ids:
            domain.append(('id', 'in', rule_ids))
        rules = self.search(domain)
        for rule in rules:
            try:
                rule.action_autovacuum(limit=limit)
                if auto_commit:
                    self.env.cr.commit()  # pylint: disable=invalid-commit
            except Exception as e:
                if not auto_commit:
                    raise
                msg_pattern = (
                    "Something went wrong processing sales autovacuum rule "
                    + "details. Rule ID: %s, error:\n%s"
                )
                _logger.error(msg_pattern, rule.id, e, exc_info=True)
                err = get_formatted_exception()
                rule.message_post(body=msg_pattern % (rule.id, err))

    def find_sale_orders(self, limit=None):
        self.ensure_one()
        domain = self._prepare_final_domain()
        return self.env['sale.order'].search(domain, limit=limit)

    def _get_last_updated_datetime(self):
        return datetime.now() - timedelta(days=self.days)

    def _prepare_base_domain(self):
        self.ensure_one()
        date_fname = self.field_date_updated_id.name
        dt = self._get_last_updated_datetime()
        domain = Domain(date_fname, '<', dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        domain_method = getattr(
            self, f"_prepare_base_domain_action_{self.action}", None
        )
        if domain_method is not None:
            # domain = Domain.AND([domain, domain_method()])
            domain &= domain_method()
        return domain

    def _prepare_base_domain_action_cancel(self):
        self.ensure_one()
        return Domain('state', 'in', ('draft', 'sent'))

    def _prepare_base_domain_action_unlink(self):
        self.ensure_one()
        return Domain('state', '=', 'draft')

    def _prepare_final_domain(self):
        self.ensure_one()
        base_domain = self._prepare_base_domain()
        domain = Domain(ast.literal_eval(self.domain))
        return Domain.AND([base_domain, domain])

    def _action_autovacuum_cancel(self, sales):
        sale_count = len(sales)
        sales_ref = self._get_sales_ref(sales)
        res = sales._action_cancel()
        self._post_autovacuum_message(sale_count, 'cancelled', sales_ref)
        return res

    def _action_autovacuum_unlink(self, sales):
        sale_count = len(sales)
        sales_ref = self._get_sales_ref(sales)
        res = sales.unlink()
        self._post_autovacuum_message(sale_count, 'deleted', sales_ref)
        return res

    def _get_sales_ref(self, sales):
        names = sorted(sales.mapped('name'))
        return ', '.join(names)

    def _post_autovacuum_message(self, sale_count, action_word, sales_ref):
        self.ensure_one()
        return self.message_post(
            body=self.env._(
                '%(sale_count)s sale quote(s) %(action_word)s: %(sales_ref)s',
                sale_count=sale_count,
                action_word=action_word,
                sales_ref=sales_ref,
            )
        )

    def _validate_autovacuum(self):
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(
                self.env._("Autovacuum rule must be in In Progress State to run!")
            )
