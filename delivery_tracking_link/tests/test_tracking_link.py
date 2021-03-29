from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestTrackingLink(SavepointCase):
    """Test class for custom tracking links."""

    @classmethod
    def setUpClass(cls):
        """Set up data."""
        super().setUpClass()
        cls.tracking_link_demo = cls.env.ref(
            'delivery_tracking_link.delivery_tracking_link_demo'
        )
        cls.picking_1 = cls.env.ref('stock.outgoing_shipment_main_warehouse6')
        cls.carrier_normal = cls.env.ref('delivery.normal_delivery_carrier')
        cls.carrier_normal.tracking_link_id = cls.tracking_link_demo.id

    def test_01_generate_tracking_link(self):
        """Generate link when picking has carrier with custom link.

        Case 1: carrier_tracking_ref=False
        Case 2: carrier_tracking_ref='123456'
        """
        # Case 1.
        self.picking_1.carrier_id = self.carrier_normal.id
        link = self.carrier_normal.get_tracking_link(self.picking_1)
        self.assertEqual(link, 'https://some-domain.com/track/False')
        # Case 2.
        self.picking_1.carrier_tracking_ref = '123456'
        link = self.carrier_normal.get_tracking_link(self.picking_1)
        self.assertEqual(link, 'https://some-domain.com/track/123456')

    def test_02_generate_tracking_link(self):
        """Try to generate link when no tracking link record is set.

        Case 1: delivery_type='fixed'
        Case 2: delivery_type='base_on_rule'
        """
        # Case 1.
        self.picking_1.carrier_id = self.carrier_normal.id
        self.carrier_normal.tracking_link_id = False
        link = self.carrier_normal.get_tracking_link(self.picking_1)
        self.assertEqual(link, False)
        # Case 2.
        self.carrier_normal.delivery_type = 'base_on_rule'
        link = self.carrier_normal.get_tracking_link(self.picking_1)
        self.assertEqual(link, False)

    def test_03_generate_tracking_link(self):
        """Try to generate link with incorrect format.

        Case: incorrect placeholder.
        """
        self.picking_1.carrier_id = self.carrier_normal.id
        self.tracking_link_demo.url_format = (
            'https://some-url.com/{picking2.name}'
        )
        with self.assertRaises(ValidationError):
            self.carrier_normal.get_tracking_link(self.picking_1)
