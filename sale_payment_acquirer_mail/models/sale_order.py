from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _find_mail_template(self, force_confirmation_template=False):
        mail_tmpl_id = self.env.context.get(
            'force_mail_template_sale_confirm_id'
        )
        if mail_tmpl_id:
            return mail_tmpl_id
        return super()._find_mail_template(
            force_confirmation_template=force_confirmation_template
        )
