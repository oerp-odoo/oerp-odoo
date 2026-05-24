from unittest.mock import patch

from odoo.fields import Command, Domain
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.delivery_3pl.utils.invoice import invoice_3pl_order


@tagged('-at_install', 'post_install')
class TestInvoice3plOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.ProductProduct = cls.env['product.product']
        cls.AccountJournal = cls.env['account.journal']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.AccountMoveSendWizard = cls.env['account.move.send.wizard']
        cls.company_main = cls.env.ref('base.main_company')
        cls.journal_bank_1 = cls.AccountJournal.search(
            Domain('company_id', '=', cls.company_main.id)
            & Domain('type', '=', 'bank'),
            limit=1,
        )
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.product_1 = cls.ProductProduct.create({'name': 'MY-PRODUCT-1'})
        cls.sale_1 = cls.SaleOrder.create(
            {
                'partner_id': cls.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': cls.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        cls.sale_1.action_confirm()
        cls.tpl_service_demo_1 = cls.TplService.create(
            {'journal_id': cls.journal_bank_1.id}
        )

    def test_01_invoice_3pl_order_invoice_state_target_draft(self):
        # WHEN
        invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'draft')
        self.assertEqual(invoice.payment_state, 'not_paid')
        # msg_bodies = invoice.message_ids.mapped('body')
        # self.assertFalse(any('blabla'))

    def test_02_invoice_3pl_order_invoice_state_target_open(self):
        # GIVEN
        self.tpl_service_demo_1.invoice_state_target = 'open'
        # WHEN
        invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.payment_state, 'not_paid')

    def test_03_invoice_3pl_order_invoice_state_target_paid(self):
        # GIVEN
        self.tpl_service_demo_1.invoice_state_target = 'paid'
        # WHEN
        with patch.object(
            type(self.AccountMoveSendWizard), 'action_send_and_print'
        ) as m:
            invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'posted')
        self.assertIn(invoice.payment_state, ('paid', 'in_payment'))
        m.assert_not_called()

    def test_04_invoice_3pl_order_invoice_state_email_open(self):
        # GIVEN
        self.tpl_service_demo_1.write(
            {'invoice_state_target': 'open', 'invoice_state_email': 'open'}
        )
        # WHEN
        with patch.object(
            type(self.AccountMoveSendWizard), 'action_send_and_print'
        ) as m:
            invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(invoice.payment_state, 'not_paid')
        m.assert_called_once()

    def test_05_invoice_3pl_order_invoice_state_email_paid(self):
        # GIVEN
        self.tpl_service_demo_1.write(
            {'invoice_state_target': 'paid', 'invoice_state_email': 'paid'}
        )
        # WHEN
        with patch.object(
            type(self.AccountMoveSendWizard), 'action_send_and_print'
        ) as m:
            invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'posted')
        self.assertIn(invoice.payment_state, ('paid', 'in_payment'))
        m.assert_called_once()

    def test_06_invoice_3pl_order_invoice_state_email_paid_inv_not_paid(self):
        # GIVEN
        self.tpl_service_demo_1.write(
            {'invoice_state_target': 'open', 'invoice_state_email': 'paid'}
        )
        # WHEN
        with patch.object(
            type(self.AccountMoveSendWizard), 'action_send_and_print'
        ) as m:
            invoice_3pl_order(self.sale_1, self.tpl_service_demo_1)
        # THEN
        invoice = self.sale_1.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, 'posted')
        self.assertIn(invoice.payment_state, 'not_paid')
        m.assert_not_called()
