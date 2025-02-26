from odoo import _, api, models
from odoo.exceptions import ValidationError

from .res_config_settings import (
    CFG_PARAM_SALE_NAME_UNIQ,
    CFG_PARAM_SALE_NAME_UNIQ_SCOPE,
    DEFAULT_SCOPE,
)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('name', 'company_id')
    def _check_name(self):
        if (
            not self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_SALE_NAME_UNIQ)
        ):
            return
        for rec in self:
            if rec.sudo().search(
                rec._prepare_unique_name_domain(),
                limit=1,
            ):
                raise ValidationError(
                    _("Sale Order with this number (%s) already exists!", rec.name)
                )

    def _prepare_unique_name_domain(self):
        self.ensure_one()
        scope = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param(CFG_PARAM_SALE_NAME_UNIQ_SCOPE, default=DEFAULT_SCOPE)
        )
        domain = [
            ('name', '=', self.name),
            ('id', '!=', self.id),
        ]
        if scope == 'company':
            domain.append(('company_id', '=', self.company_id.id))
        return domain
