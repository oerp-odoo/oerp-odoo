from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMrpOptionalTracking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.product_1 = cls.ProductProduct.create(
            {'name': 'MY-PRODUCT-1', 'type': 'product'}
        )

    def test_01_mrp_tracking_ok(self):
        # WHEN
        self.product_1.mrp_tracking = 'serial'
        # THEN
        self.assertEqual(self.product_1.mrp_tracking, 'serial')
        self.assertEqual(self.product_1.tracking, 'none')

    def test_02_mrp_tracking_original_trackin_used(self):
        # GIVEN
        self.product_1.tracking = 'serial'
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"MRP Tracking can only be used when standard Tracking is not used!",
        ):
            self.product_1.mrp_tracking = 'serial'

    def test_03_mrp_tracking_via_original_tracking_as_mrp_production_model(self):
        # GIVEN
        self.product_1.mrp_tracking = 'serial'
        # WHEN
        tracking = self.product_1.with_context(
            params={'model': 'mrp.production'}
        ).tracking
        # THEN
        self.assertEqual(tracking, 'serial')

    def test_04_mrp_tracking_via_original_tracking_not_as_mrp_production_model(self):
        # GIVEN
        self.product_1.mrp_tracking = 'serial'
        # WHEN
        tracking = self.product_1.with_context(
            params={'model': 'stock.picking'}
        ).tracking
        # THEN
        self.assertEqual(tracking, 'none')
