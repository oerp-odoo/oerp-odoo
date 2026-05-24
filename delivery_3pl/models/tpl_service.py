from odoo import fields, models
from odoo.exceptions import ValidationError


class TplService(models.Model):
    _name = 'tpl.service'
    _description = "3PL Service"
    _rec_name = 'integration'

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda s: s.env.user.company_id,
    )
    integration = fields.Selection([])
    http_client_profile_id = fields.Many2one('http.client.profile', copy=False)
    # TODO: add service matching filter to use sale_order as a context.
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

    def get_3pl_service(self, sale_order, integration=None, raise_not_found=True):
        service_matchers = self.get_3pl_service_matchers()
        if integration is not None:
            try:
                service_matchers = {integration: service_matchers[integration]}
            except KeyError:
                raise ValidationError(
                    self.env._(
                        "No 3PL service matcher found for integration %s", integration
                    )
                )
        for service_matcher in service_matchers.values():
            service = service_matcher(sale_order)
            if service:
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

    def get_3pl_service_matchers(self):
        """Return 3PL service matchers.

        Key is unique string and value is function that expects sale.order
        record as input.
        """
        return {}
