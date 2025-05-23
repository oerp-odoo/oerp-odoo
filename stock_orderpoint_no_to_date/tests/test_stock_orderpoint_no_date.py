from odoo.tests.common import TransactionCase


class TestStockOrderpointNoDate(TransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.StockWarehouseOrderpoint = cls.env['stock.warehouse.orderpoint']
        cls.ProductProduct = cls.env['product.product']
        cls.stock_location_stock = cls.env.ref('stock.stock_location_stock')
        cls.company_main = cls.env.ref('base.main_company')
        cls.product_1 = cls.ProductProduct.create(
            {'name': 'MY-PRODUCT-1', 'type': 'product'}
        )
        cls.orderpoint_1 = cls.StockWarehouseOrderpoint.create(
            {
                'product_id': cls.product_1.id,
                'location_id': cls.stock_location_stock.id,
            }
        )

    def test_01_orderpoint_product_ctx_no_to_date(self):
        # GIVEN
        self.company_main.orderpoint_no_to_date = True
        # WHEN
        res = self.orderpoint_1._get_product_context()
        # THEN
        self.assertNotIn('to_date', res)

    def test_02_orderpoint_product_ctx_with_to_date(self):
        # GIVEN
        self.company_main.orderpoint_no_to_date = False
        # WHEN
        res = self.orderpoint_1._get_product_context()
        # THEN
        self.assertIn('to_date', res)
