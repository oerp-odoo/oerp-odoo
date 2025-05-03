from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockChainAutoDone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockLocation = cls.env['stock.location']
        cls.StockQuant = cls.env['stock.quant']
        cls.StockPicking = cls.env['stock.picking']
        cls.StockMove = cls.env['stock.move']
        cls.StockChainRule = cls.env['stock.chain.rule']
        cls.ProductProduct = cls.env['product.product']
        cls.product_1 = cls.ProductProduct.create(
            {'name': 'MY-PRODUCT-1', 'type': 'product'}
        )
        cls.picking_out = cls.env.ref('stock.picking_type_out')
        # View location
        cls.location_physical = cls.env.ref('stock.stock_location_locations')
        cls.location_transit = cls.StockLocation.create(
            {
                'name': 'MY-TRANSIT',
                'usage': 'transit',
                'location_id': cls.location_physical.id,
            }
        )
        # WH/Stock
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_customers = cls.env.ref('stock.stock_location_customers')
        cls.chain_rule_1 = cls.StockChainRule.create(
            {'location_id': cls.location_transit.id}
        )
        cls.picking_1, cls.picking_2 = cls.StockPicking.create(
            [
                {
                    'picking_type_id': cls.picking_out.id,
                    'location_id': cls.location_stock.id,
                    'location_dest_id': cls.location_transit.id,
                },
                {
                    'picking_type_id': cls.picking_out.id,
                    'location_id': cls.location_transit.id,
                    'location_dest_id': cls.location_customers.id,
                },
            ]
        )

    def test_01_picking_chain_auto_finish(self):
        # GIVEN
        self.StockQuant.create(
            {
                'product_id': self.product_1.id,
                'quantity': 10,
                'location_id': self.location_stock.id,
            }
        )
        move_2 = self.StockMove.create(
            {
                'name': 'MY-MOVE-2',
                'picking_id': self.picking_2.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_transit.id,
                'location_dest_id': self.location_customers.id,
            }
        )
        self.StockMove.create(
            {
                'name': 'MY-MOVE-1',
                'picking_id': self.picking_1.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_transit.id,
                'move_dest_ids': [Command.link(move_2.id)],
            }
        )
        # To setup linked moves and put second one in waiting state.
        (self.picking_1 | self.picking_2).action_confirm()
        # WHEN
        self.picking_1.action_assign()
        self.picking_1.button_validate()
        # THEN
        self.assertEqual(self.picking_1.state, 'done')
        self.assertEqual(self.picking_2.state, 'done')

    def test_02_picking_chain_auto_finish_no_rule(self):
        # GIVEN
        self.chain_rule_1.active = False
        self.StockQuant.create(
            {
                'product_id': self.product_1.id,
                'quantity': 10,
                'location_id': self.location_stock.id,
            }
        )
        move_2 = self.StockMove.create(
            {
                'name': 'MY-MOVE-2',
                'picking_id': self.picking_2.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_transit.id,
                'location_dest_id': self.location_customers.id,
            }
        )
        self.StockMove.create(
            {
                'name': 'MY-MOVE-1',
                'picking_id': self.picking_1.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_transit.id,
                'move_dest_ids': [Command.link(move_2.id)],
            }
        )
        (self.picking_1 | self.picking_2).action_confirm()
        # WHEN
        self.picking_1.action_assign()
        self.picking_1.button_validate()
        # THEN
        self.assertEqual(self.picking_1.state, 'done')
        self.assertEqual(self.picking_2.state, 'assigned')

    def test_03_picking_chain_auto_finish_no_match(self):
        # GIVEN
        self.chain_rule_1.location_id = self.location_customers.id
        self.StockQuant.create(
            {
                'product_id': self.product_1.id,
                'quantity': 10,
                'location_id': self.location_stock.id,
            }
        )
        move_2 = self.StockMove.create(
            {
                'name': 'MY-MOVE-2',
                'picking_id': self.picking_2.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_transit.id,
                'location_dest_id': self.location_customers.id,
            }
        )
        self.StockMove.create(
            {
                'name': 'MY-MOVE-1',
                'picking_id': self.picking_1.id,
                'product_id': self.product_1.id,
                'product_uom_qty': 5,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_transit.id,
                'move_dest_ids': [Command.link(move_2.id)],
            }
        )
        (self.picking_1 | self.picking_2).action_confirm()
        # WHEN
        self.picking_1.action_assign()
        self.picking_1.button_validate()
        # THEN
        self.assertEqual(self.picking_1.state, 'done')
        self.assertEqual(self.picking_2.state, 'assigned')
