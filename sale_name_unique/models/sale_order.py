from odoo import _, api, models
from odoo.exceptions import ValidationError

from .res_config_settings import CFG_PARAM_SALE_NAME_UNIQ


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
            if rec.search(
                [
                    ('name', '=', rec.name),
                    ('company_id', '=', rec.company_id.id),
                    ('id', '!=', rec.id),
                ],
                limit=1,
            ):
                raise ValidationError(
                    _("Sale Order with this number (%s) already exists!", rec.name)
                )
