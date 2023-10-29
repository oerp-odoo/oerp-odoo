import ast

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    mail_template_sale_confirm_id = fields.Many2one(
        'mail.template',
        string="Custom Sale Confirmation Template",
        domain=[('model_id.model', '=', 'sale.order')],
    )
    mail_template_sale_confirm_ctx = fields.Char(
        default="{}",
        string="Custom Sale Confirmation Template Context",
        help="Must be a dictionary. e.g {'proforma': True}",
    )

    @api.constrains('mail_template_sale_confirm_ctx')
    def _check_mail_template_sale_confirm_ctx(self):
        for rec in self:
            if rec.mail_template_sale_confirm_ctx:
                ctx_str = rec.mail_template_sale_confirm_ctx
                msg = _("Context must be dictionary. Got: %s", ctx_str)
                try:
                    ctx = ast.literal_eval(ctx_str)
                except Exception:
                    raise ValidationError(msg)
                if not isinstance(ctx, dict):
                    raise ValidationError(msg)
