from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleConfirmTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PaymentTransaction = cls.env['payment.transaction']
        # draft state.
        cls.sale_3 = cls.env.ref('sale.sale_order_3')
        cls.payment_acquirer_transfer = cls.env.ref(
            'payment.payment_acquirer_transfer'
        )
        cls.mail_template_quote = cls.env.ref('sale.email_template_edi_sale')

    def test_01_sale_payment_tx_w_custom_mail_confirm_template(self):
        # GIVEN
        self.payment_acquirer_transfer.mail_template_sale_confirm_id = (
            self.mail_template_quote.id
        )
        ref = f'{self.sale_3}-111'
        self.PaymentTransaction.create(
            {
                'acquirer_id': self.payment_acquirer_transfer.id,
                'reference': ref,
                'amount': self.sale_3.amount_total,
                'currency_id': self.sale_3.currency_id.id,
                'partner_id': self.sale_3.partner_invoice_id.id,
                'operation': 'online_redirect',
                'landing_route': '/shop/payment/validate',
                'sale_order_ids': [(6, 0, self.sale_3.ids)],
            }
        )
        # WHEN
        self.env['payment.transaction']._handle_feedback_data(
            'transfer', {'reference': ref}
        )
        # THEN
        self.assertEqual(self.sale_3.state, 'sent')
        # Should have used template specified on payment acquirer.
        body = self.sale_3.message_ids[0].body
        self.assertIn('quotation', body)
        self.assertIn('ready for review', body)

    def test_02_sale_payment_tx_w_custom_mail_confirm_template_w_ctx(self):
        # GIVEN
        self.payment_acquirer_transfer.write(
            {
                'mail_template_sale_confirm_id': self.mail_template_quote.id,
                'mail_template_sale_confirm_ctx': "{'proforma': True}",
            }
        )
        ref = f'{self.sale_3}-111'
        self.PaymentTransaction.create(
            {
                'acquirer_id': self.payment_acquirer_transfer.id,
                'reference': ref,
                'amount': self.sale_3.amount_total,
                'currency_id': self.sale_3.currency_id.id,
                'partner_id': self.sale_3.partner_invoice_id.id,
                'operation': 'online_redirect',
                'landing_route': '/shop/payment/validate',
                'sale_order_ids': [(6, 0, self.sale_3.ids)],
            }
        )
        # WHEN
        self.env['payment.transaction']._handle_feedback_data(
            'transfer', {'reference': ref}
        )
        # THEN
        self.assertEqual(self.sale_3.state, 'sent')
        # Should have used template specified on payment acquirer.
        body = self.sale_3.message_ids[0].body
        self.assertIn('Pro forma invoice for quotation', body)
        self.assertNotIn('ready for review', body)

    def test_03_sale_payment_tx_w_default_mail_confirm_template(self):
        # GIVEN
        ref = f'{self.sale_3}-111'
        self.PaymentTransaction.create(
            {
                'acquirer_id': self.payment_acquirer_transfer.id,
                'reference': ref,
                'amount': self.sale_3.amount_total,
                'currency_id': self.sale_3.currency_id.id,
                'partner_id': self.sale_3.partner_invoice_id.id,
                'operation': 'online_redirect',
                'landing_route': '/shop/payment/validate',
                'sale_order_ids': [(6, 0, self.sale_3.ids)],
            }
        )
        # WHEN
        self.env['payment.transaction']._handle_feedback_data(
            'transfer', {'reference': ref}
        )
        # THEN
        self.assertEqual(self.sale_3.state, 'sent')
        body = self.sale_3.message_ids[0].body
        self.assertIn('order', body)
        self.assertIn(
            'It will be confirmed when the payment is received', body
        )

    def test_04_payment_transaction_ctx_wrong_type(self):
        with self.assertRaises(ValidationError):
            self.payment_acquirer_transfer.mail_template_sale_confirm_ctx = (
                "123"
            )

    def test_05_payment_transaction_ctx_cant_eval(self):
        with self.assertRaises(ValidationError):
            self.payment_acquirer_transfer.mail_template_sale_confirm_ctx = (
                "xxx"
            )
