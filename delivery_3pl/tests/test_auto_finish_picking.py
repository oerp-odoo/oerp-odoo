from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from ..utils import auto_finish_picking


class TestAutoFinishPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPicking = cls.env['stock.picking']
        cls.StockMove = cls.env['stock.move']
        cls.ProductProduct = cls.env['product.product']
        cls.StockQuant = cls.env['stock.quant']
        cls.stock_picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.stock_location_stock = cls.env.ref('stock.stock_location_stock')
        cls.stock_location_customers = cls.env.ref('stock.stock_location_customers')
        cls.product_1 = cls.ProductProduct.create(
            {'name': 'MY-PRODUCT-1', 'type': 'product'}
        )
        cls.picking_1 = cls.StockPicking.create(
            {
                'picking_type_id': cls.stock_picking_type_out.id,
                'location_id': cls.stock_location_stock.id,
                'location_dest_id': cls.stock_location_customers.id,
            }
        )
        cls.stock_move_1 = cls.StockMove.create(
            {
                'picking_id': cls.picking_1.id,
                'name': 'MY-STOCK-MOVE-1',
                'product_id': cls.product_1.id,
                'product_uom_qty': 10,
                'product_uom': cls.product_1.uom_id.id,
                'location_id': cls.stock_location_stock.id,
                'location_dest_id': cls.stock_location_customers.id,
            }
        )
        cls.picking_1.action_confirm()

    def test_01_auto_finish_picking_enough_stock(self):
        # GIVEN
        self.StockQuant.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.stock_location_stock.id,
                "quantity": 30.0,
            }
        )
        # WHEN
        auto_finish_picking(self.picking_1)
        # THEN
        self.assertEqual(self.picking_1.state, 'done')
        move_line = self.picking_1.move_line_ids
        self.assertEqual(len(move_line), 1)
        self.assertEqual(move_line.product_uom_qty, 0)
        self.assertEqual(move_line.qty_done, 10)

    def test_02_auto_finish_picking_not_enough_stock(self):
        # GIVEN
        self.StockQuant.create(
            {
                "product_id": self.product_1.id,
                "location_id": self.stock_location_stock.id,
                "quantity": 6.0,
            }
        )
        # WHEN
        auto_finish_picking(self.picking_1)
        # THEN
        self.assertEqual(self.picking_1.state, 'assigned')
        move_line = self.picking_1.move_line_ids
        self.assertEqual(len(move_line), 1)
        self.assertEqual(move_line.product_uom_qty, 6)
        self.assertEqual(move_line.qty_done, 6)

    def test_03_auto_finish_picking_no_stock_raise(self):
        # GIVEN
        # WHEN
        with self.assertRaisesRegex(
            UserError,
            r"You cannot validate a transfer if no quantities are reserved nor done",
        ):
            auto_finish_picking(self.picking_1)

    def test_04_auto_finish_picking_no_stock_log(self):
        # GIVEN
        # WHEN
        auto_finish_picking(self.picking_1, raise_exc=False)
        # THEN
        self.assertEqual(self.picking_1.state, 'confirmed')
        self.assertEqual(len(self.picking_1.move_line_ids), 0)
