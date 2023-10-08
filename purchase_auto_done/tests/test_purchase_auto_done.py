from odoo.tests import common

from ..models.res_config_settings import CFG_PARAM_PO_AUTO_DONE


@common.tagged('post_install', '-at_install')
class TestPurchaseAutoDone(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.ProductProduct = cls.env['product.product']
        cls.AccountPaymentRegister = cls.env['account.payment.register']
        cls.AccountMove = cls.env['account.move']
        cls.AccountJournal = cls.env['account.journal']
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.journal_1 = cls._get_journals('bank')[0]
        # Method to send payments.
        # cls.payment_method_out = cls.env.ref(
        #     'account.account_payment_method_manual_out')
        cls.product_1 = cls.ProductProduct.create(
            {
                'name': 'My Product 1',
                'type': 'product',
                'default_code': 'MP1',
            }
        )
        cls.purchase_1 = cls.PurchaseOrder.create(
            {
                'partner_id': cls.partner_azure.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_1.id,
                            'name': 'Product 1',
                            'product_qty': 10,
                            'price_unit': 1,
                        },
                    )
                ],
            }
        )
        cls.IrConfigParameter.set_param(CFG_PARAM_PO_AUTO_DONE, True)

    @classmethod
    def _get_journals(cls, type_):
        return cls.AccountJournal.search([('type', '=', type_)])

    def test_01_purchase_auto_done_on_pay(self):
        # GIVEN
        self.purchase_1.button_confirm()
        # First deliver
        picking_1 = self.purchase_1.picking_ids[0]
        picking_1.move_line_ids[0].qty_done = 10
        picking_1._action_done()
        # WHEN
        self.purchase_1.with_context(
            default_invoice_date='2022-02-19',
            default_date='2022-02-19',
        ).action_create_invoice()
        invoice = self.purchase_1.invoice_ids[0]
        invoice.action_post()
        # Create payment record and register payment.
        payment_register = (
            self.AccountPaymentRegister.with_context(
                active_ids=[invoice.id], active_model='account.move'
            )
            .create({'journal_id': self.journal_1.id})
        )
        payment_register.action_create_payments()
        # THEN
        self.assertEqual(self.purchase_1.state, 'done')

    def test_02_purchase_auto_done_on_picking_done(self):
        # GIVEN
        self.purchase_1.button_confirm()
        # First pay
        # To be able to pay not delivered quantities
        self.purchase_1.order_line[0].qty_to_invoice = 10
        self.purchase_1.with_context(
            default_invoice_date='2022-02-19',
            default_date='2022-02-19',
        ).action_create_invoice()
        invoice = self.purchase_1.invoice_ids[0]
        invoice.action_post()
        # Create payment record and register payment.
        payment_register = (
            self.AccountPaymentRegister.with_context(
                active_ids=[invoice.id], active_model='account.move'
            )
            .create({'journal_id': self.journal_1.id})
        )
        payment_register.action_create_payments()
        picking_1 = self.purchase_1.picking_ids[0]
        # WHEN
        picking_1.move_line_ids[0].qty_done = 10
        picking_1._action_done()
        # THEN
        self.assertEqual(self.purchase_1.state, 'done')

    def test_03_purchase_no_auto_done_disabled(self):
        # GIVEN
        self.IrConfigParameter.set_param(CFG_PARAM_PO_AUTO_DONE, False)
        self.purchase_1.button_confirm()
        # First deliver
        picking_1 = self.purchase_1.picking_ids[0]
        picking_1.move_line_ids[0].qty_done = 10
        picking_1._action_done()
        # WHEN
        self.purchase_1.with_context(
            default_invoice_date='2022-02-19',
            default_date='2022-02-19',
        ).action_create_invoice()
        invoice = self.purchase_1.invoice_ids[0]
        invoice.action_post()
        # Create payment record and register payment.
        payment_register = (
            self.AccountPaymentRegister.with_context(
                active_ids=[invoice.id], active_model='account.move'
            )
            .create({'journal_id': self.journal_1.id})
        )
        payment_register.action_create_payments()
        # THEN
        self.assertEqual(self.purchase_1.state, 'purchase')

    def test_04_purchase_no_auto_done_partially_received(self):
        # GIVEN
        self.purchase_1.button_confirm()
        # First deliver
        picking_1 = self.purchase_1.picking_ids[0]
        # Not fully delivered
        picking_1.move_line_ids[0].qty_done = 4
        picking_1._action_done()
        # WHEN
        self.purchase_1.with_context(
            default_invoice_date='2022-02-19',
            default_date='2022-02-19',
        ).action_create_invoice()
        invoice = self.purchase_1.invoice_ids[0]
        invoice.action_post()
        # Create payment record and register payment.
        payment_register = (
            self.AccountPaymentRegister.with_context(
                active_ids=[invoice.id], active_model='account.move'
            )
            .create({'journal_id': self.journal_1.id})
        )
        payment_register.action_create_payments()
        # THEN
        self.assertEqual(self.purchase_1.state, 'purchase')

    def test_05_purchase_no_auto_done_partially_paid(self):
        # GIVEN
        self.purchase_1.button_confirm()
        # First pay
        # To be able to pay not delivered quantities
        self.purchase_1.order_line[0].qty_to_invoice = 4
        self.purchase_1.with_context(
            default_invoice_date='2022-02-19',
            default_date='2022-02-19',
        ).action_create_invoice()
        invoice = self.purchase_1.invoice_ids[0]
        invoice.action_post()
        # Create payment record and register payment.
        payment_register = (
            self.AccountPaymentRegister.with_context(
                active_ids=[invoice.id], active_model='account.move'
            )
            .create({'journal_id': self.journal_1.id})
        )
        payment_register.action_create_payments()
        picking_1 = self.purchase_1.picking_ids[0]
        # WHEN
        picking_1.move_line_ids[0].qty_done = 10
        picking_1._action_done()
        # THEN
        self.assertEqual(self.purchase_1.state, 'purchase')
