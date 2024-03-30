from odoo import api, fields, models
from odoo.osv import expression


class AccountFiscalPosition(models.Model):
    """Extend to add fiscal position find logic by company_type."""

    _inherit = 'account.fiscal.position'

    company_type = fields.Selection(
        [('person', "Individual"), ('company', "Company")],
        help="Apply only if partner matches company type",
    )

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        """Extend to pass company_type context as extra filter."""
        partner_chosen_id = delivery_id or partner_id
        if partner_chosen_id:
            partner = (
                self.env['res.partner'].browse(partner_chosen_id).commercial_partner_id
            )
            self = self.with_context(partner_is_company=partner.is_company)
            fp = super(
                AccountFiscalPosition,
                self.with_context(partner_company_type=partner.company_type),
            ).get_fiscal_position(partner_id, delivery_id=delivery_id)
            if fp:
                return fp
        return super(AccountFiscalPosition, self).get_fiscal_position(
            partner_id, delivery_id=delivery_id
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Extend to use partner_company_type context in domain."""
        partner_company_type = self._context.get('partner_company_type')
        if partner_company_type:
            args = expression.AND([args, [('company_type', '=', partner_company_type)]])
        return super(AccountFiscalPosition, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )
