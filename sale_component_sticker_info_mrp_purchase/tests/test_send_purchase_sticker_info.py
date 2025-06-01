from odoo.tests.common import TransactionCase


class TestSendPurchaseStickerInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.ProductProduct = cls.env['product.product']
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.PurchaseComponentStickerInfo = cls.env['purchase.component.sticker.info']
        cls.Wizard = cls.env['purchase.component.sticker.info.export']
        cls.partner_vendor_1 = cls.ResPartner.create(
            [
                {'name': 'MY-VENDOR-1', 'is_company': True},
            ]
        )
        cls.partner_vendor_contact_1 = cls.ResPartner.create(
            {
                'name': 'MY-VENDOR-CONTACT-1',
                'parent_id': cls.partner_vendor_1.id,
                'components_doc_receiver': True,
                'email': 'my@example.com',
            }
        )
        cls.product_1, cls.product_2 = cls.ProductProduct.create(
            [
                {
                    'name': 'P1',
                    "default_code": "C1",
                },
                {
                    'name': 'P2',
                    "default_code": "C2",
                },
            ]
        )
        cls.purchase_1 = cls.PurchaseOrder.create(
            [
                {
                    'partner_id': cls.partner_vendor_1.id,
                    'partner_ref': 'MY-PARTNER-REF-1',
                }
            ]
        )

    def test_01_send_purchase_sicker_info_to_partner(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2.0,
                    'component_sticker_info': 'A-1 S001 [QTY:1.0]; A-2 S001 [QTY:1.0]',
                },
            )
        ]
        # WHEN
        self.purchase_1.button_confirm()
        # THEN
        msg = self.purchase_1.message_ids[0]
        self.assertEqual(msg.subject, "Required quantity of components")
        self.assertIn("Here is a list of needed components", msg.body)
        self.assertEqual(msg.partner_ids, self.partner_vendor_contact_1)
        self.assertEqual(len(msg.attachment_ids), 1)

    def test_02_not_enabled_to_send_purchase_sicker_info_to_partner(self):
        # GIVEN
        self.partner_vendor_contact_1.components_doc_receiver = False
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2.0,
                    'component_sticker_info': 'A-1 S001 [QTY:1.0]; A-2 S001 [QTY:1.0]',
                },
            )
        ]
        # WHEN
        self.purchase_1.button_confirm()
        # THEN
        msg = self.purchase_1.message_ids[0]
        self.assertNotEqual(msg.subject, "Required quantity of components")
