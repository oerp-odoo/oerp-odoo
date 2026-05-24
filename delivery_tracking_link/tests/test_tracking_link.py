from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTrackingLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DeliveryTrackingLink = cls.env['delivery.tracking.link']
        cls.DeliveryCarrier = cls.env['delivery.carrier']
        cls.StockPicking = cls.env['stock.picking']
        cls.ProductProduct = cls.env['product.product']
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.product_delivery = cls.ProductProduct.create(
            {'name': 'MY-DELIVERY-PRODUCT-1'}
        )
        cls.carrier_1 = cls.DeliveryCarrier.create(
            {
                'name': 'MY-CARRIER-1',
                'delivery_type': 'fixed',
                'product_id': cls.product_delivery.id,
            }
        )
        cls.tracking_link_1 = cls.DeliveryTrackingLink.create(
            {
                'name': 'MY-TRACKING-LINK-1',
                'url_format': (
                    'https://some-domain.com/track/{picking.carrier_tracking_ref}'
                ),
            }
        )
        cls.picking_1 = cls.StockPicking.create(
            {
                'picking_type_id': cls.picking_type_out.id,
            }
        )
        cls.carrier_1.tracking_link_id = cls.tracking_link_1.id

    def test_01_generate_tracking_link_ref_not_set(self):
        # GIVEN
        self.picking_1.carrier_id = self.carrier_1.id
        # WHEN
        link = self.carrier_1.get_tracking_link(self.picking_1)
        # THEN
        self.assertEqual(link, 'https://some-domain.com/track/False')

    def test_02_generate_tracking_link_ref_set(self):
        # GIVEN
        self.picking_1.carrier_id = self.carrier_1.id
        self.picking_1.carrier_tracking_ref = '123456'
        # WHEN
        link = self.carrier_1.get_tracking_link(self.picking_1)
        # THEN
        self.assertEqual(link, 'https://some-domain.com/track/123456')

    def test_03_generate_tracking_link_no_link_dtype_fixed(self):
        # GIVEN
        self.picking_1.carrier_id = self.carrier_1.id
        self.carrier_1.tracking_link_id = False
        # WHEN
        link = self.carrier_1.get_tracking_link(self.picking_1)
        # THEN
        self.assertEqual(link, False)

    def test_04_generate_tracking_link_no_link_dtype_base_on_rule(self):
        # GIVEN
        self.picking_1.carrier_id = self.carrier_1.id
        self.carrier_1.write(
            {
                'tracking_link_id': False,
                'delivery_type': 'base_on_rule',
            }
        )
        # WHEN
        link = self.carrier_1.get_tracking_link(self.picking_1)
        # THEN
        self.assertEqual(link, False)

    def test_05_generate_tracking_link_incorrect_format(self):
        # GIVEN
        self.picking_1.carrier_id = self.carrier_1.id
        self.tracking_link_1.url_format = 'https://some-url.com/{picking2.name}'
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Tracking Links has incorrect format"
        ):
            self.carrier_1.get_tracking_link(self.picking_1)

    def test_06_carrier_tracking_url_custom(self):
        # WHEN
        self.picking_1.carrier_tracking_url_custom = 'https://some-url.com/123'
        # THEN
        self.assertEqual(
            self.picking_1.carrier_tracking_url, 'https://some-url.com/123'
        )
