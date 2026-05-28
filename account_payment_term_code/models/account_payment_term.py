from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    code = fields.Char(copy=False)

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
