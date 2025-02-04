import base64

from odoo.tests.common import TransactionCase


class TestExportPurchaseStickerInfo(TransactionCase):
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
        cls.purchase_1, cls.purchase_2 = cls.PurchaseOrder.create(
            [
                {
                    'partner_id': cls.partner_vendor_1.id,
                    'partner_ref': 'MY-PARTNER-REF-1',
                },
                {
                    'partner_id': cls.partner_vendor_1.id,
                    'partner_ref': 'MY-PARTNER-REF-2',
                },
            ]
        )

    def test_01_prepare_component_sticker_info_when_set(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2,
                    'component_sticker_info': 'A-1 S001; A-2 S001',
                },
            )
        ]
        # WHEN
        res = self.PurchaseComponentStickerInfo.prepare_data(self.purchase_1)
        # THEN
        self.assertEqual(
            res,
            [
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2,
                    'Group Name': 'A-1 S001',
                },
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2,
                    'Group Name': 'A-2 S001',
                },
            ],
        )

    def test_02_prepare_component_sticker_info_when_set_multi_po(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2,
                    'component_sticker_info': 'A-1 S001; A-2 S001',
                },
            )
        ]
        self.purchase_2.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'component_sticker_info': 'B-1 S001; B-2 S001',
                },
            )
        ]
        # WHEN
        res = self.PurchaseComponentStickerInfo.prepare_data(
            self.purchase_1 | self.purchase_2
        )
        # THEN
        self.assertEqual(
            res,
            [
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2.0,
                    'Group Name': 'A-1 S001',
                },
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2.0,
                    'Group Name': 'A-2 S001',
                },
                {
                    'Internal Reference': 'C2',
                    'Vendor Reference': 'MY-PARTNER-REF-2',
                    'Name': 'P2',
                    'Quantity': 1.0,
                    'Group Name': 'B-1 S001',
                },
                {
                    'Internal Reference': 'C2',
                    'Vendor Reference': 'MY-PARTNER-REF-2',
                    'Name': 'P2',
                    'Quantity': 1.0,
                    'Group Name': 'B-2 S001',
                },
            ],
        )

    def test_03_prepare_component_sticker_info_when_set_n_not_set(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2.0,
                    'component_sticker_info': 'A-1 S001; A-2 S001',
                },
            ),
            (
                0,
                0,
                {
                    'product_id': self.product_2.id,
                    'product_qty': 3.0,
                },
            ),
        ]
        # WHEN
        res = self.PurchaseComponentStickerInfo.prepare_data(self.purchase_1)
        # THEN
        self.assertEqual(
            res,
            [
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2.0,
                    'Group Name': 'A-1 S001',
                },
                {
                    'Internal Reference': 'C1',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P1',
                    'Quantity': 2.0,
                    'Group Name': 'A-2 S001',
                },
                {
                    'Internal Reference': 'C2',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P2',
                    'Quantity': 3.0,
                    'Group Name': None,
                },
            ],
        )

    def test_04_prepare_component_sticker_info_when_not_set(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_2.id,
                    'product_qty': 3,
                },
            ),
        ]
        # WHEN
        res = self.PurchaseComponentStickerInfo.prepare_data(self.purchase_1)
        # THEN
        self.assertEqual(
            res,
            [
                {
                    'Internal Reference': 'C2',
                    'Vendor Reference': 'MY-PARTNER-REF-1',
                    'Name': 'P2',
                    'Quantity': 3.0,
                    'Group Name': None,
                },
            ],
        )

    def test_05_export_purchase_sicker_info_to_csv(self):
        # GIVEN
        self.purchase_1.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_1.id,
                    'product_qty': 2,
                    'component_sticker_info': 'A-1 S001; A-2 S001',
                },
            )
        ]
        self.purchase_2.order_line = [
            (
                0,
                0,
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'component_sticker_info': 'B-1 S001; B-2 S001',
                },
            )
        ]
        wiz = self.Wizard.with_context(
            active_ids=(self.purchase_1 | self.purchase_2).ids,
            active_model='purchase.order',
        ).create({})
        # WHEN
        res = wiz.action_export()
        # THEN
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': (
                    f'/web/content/purchase.component.sticker.info.export/{wiz.id}/'
                    + 'data/component_sticker_info.csv?download=true'
                ),
            },
        )
        data = base64.b64decode(wiz.data).decode()
        data_lines = [d.strip() for d in data.split('\n') if d.strip()]
        self.assertEqual(len(data_lines), 5)
        self.assertEqual(
            data_lines[0],
            'Internal Reference,Vendor Reference,Name,Quantity,Group Name',
        )
        self.assertEqual(data_lines[1], 'C1,MY-PARTNER-REF-1,P1,2.0,A-1 S001')
        self.assertEqual(data_lines[2], 'C1,MY-PARTNER-REF-1,P1,2.0,A-2 S001')
        self.assertEqual(data_lines[3], 'C2,MY-PARTNER-REF-2,P2,1.0,B-1 S001')
        self.assertEqual(data_lines[4], 'C2,MY-PARTNER-REF-2,P2,1.0,B-2 S001')
