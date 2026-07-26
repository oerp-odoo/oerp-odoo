from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    code = fields.Char(copy=False)

    _code_uniq = models.Constraint(
        'unique(code)',
        'The Code must be unique!',
    )
