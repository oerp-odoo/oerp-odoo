from odoo.tests.common import TransactionCase


class TestStockMtsElseMto(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.StockQuant = cls.env['stock.quant']
        cls.StockMove = cls.env['stock.move']
        cls.StockRule = cls.env['stock.rule']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.StockWarehouseOrderpoint = cls.env['stock.warehouse.orderpoint']
        cls.company_main = cls.env.ref('base.main_company')
        cls.stock_location_stock = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_customers = cls.env.ref('stock.stock_location_customers')
        cls.stock_route_mto = cls.env.ref('stock.route_warehouse0_mto')
        # There could be multiple rules depending on modules installed, so
        # testing with WH: Stock → Customers one which should always be
        # available.
        cls.stock_rule_mts_mto = cls.stock_route_mto.rule_ids.filtered(
            lambda r: r.location_src_id == cls.stock_location_stock
            and r.location_id == cls.stock_location_customers
            and r.procure_method == 'mts_else_mto'
            and r.action == 'pull'
        )
        cls.stock_route_mto.active = True
        cls.product_1 = cls.ProductProduct.create(
            {
                'name': 'MY-PRODUCT-1',
                'type': 'product',
                'route_ids': [(6, 0, cls.stock_route_mto.ids)],
            }
        )
        cls.orderpoint_1 = cls.StockWarehouseOrderpoint.create(
            {
                'product_id': cls.product_1.id,
                'product_min_qty': 10,
                'product_max_qty': 10,
                'location_id': cls.stock_location_stock.id,
                'qty_multiple': 1,
            }
        )
        # To make Quantity on hand 10.
        cls.StockQuant.create(
            {
                'product_id': cls.product_1.id,
                'location_id': cls.stock_location_stock.id,
                'quantity': 10,
            }
        )

    def test_01_orderpoint_max_qty_perc_is_mto(self):
        # GIVEN
        self.stock_route_mto.write(
            {
                'mts_else_mto_condition': 'orderpoint_max_qty_perc',
                'orderpoint_max_qty_perc': 50.0,
            }
        )
        procurement = self.ProcurementGroup.Procurement(
            product_id=self.product_1,
            # MAX qty is 10 (on hand is also 10), so 6 is over 50%.
            product_qty=6,
            product_uom=self.product_1.uom_id,
            # Destination location
            location_id=self.stock_location_customers,
            name=self.product_1.name,
            origin='MY-ORIGIN-1',
            company_id=self.company_main,
            values={
                'group_id': self.ProcurementGroup,
                'date_planned': '2020-02-19 00:00:00',
            },
        )
        # WHEN
        self.StockRule._run_pull([(procurement, self.stock_rule_mts_mto)])
        # THEN
        moves = self.StockMove.search([('origin', '=', 'MY-ORIGIN-1')])
        # With mts_else_mto, when MTO is triggered it triggers another
        # rule, which is MTS in this case, so in total there should be
        # 2 moves.
        self.assertEqual(len(moves), 2)
        move_mto = moves.filtered(lambda r: r.procure_method == 'make_to_order')
        self.assertEqual(len(move_mto), 1)
        move_mts = moves.filtered(lambda r: r.procure_method == 'make_to_stock')
        self.assertEqual(len(move_mts), 1)

    def test_02_orderpoint_max_qty_perc_trigger_is_mts_under_threshold(self):
        # GIVEN
        self.stock_route_mto.write(
            {
                'mts_else_mto_condition': 'orderpoint_max_qty_perc',
                'orderpoint_max_qty_perc': 50.0,
            }
        )
        procurement = self.ProcurementGroup.Procurement(
            product_id=self.product_1,
            # MAX qty is 10, so 4 is under 50%.
            product_qty=4,
            product_uom=self.product_1.uom_id,
            # Destination location
            location_id=self.stock_location_customers,
            name=self.product_1.name,
            origin='MY-ORIGIN-1',
            company_id=self.company_main,
            values={
                'group_id': self.ProcurementGroup,
                'date_planned': '2020-02-19 00:00:00',
            },
        )
        # WHEN
        self.StockRule._run_pull([(procurement, self.stock_rule_mts_mto)])
        # THEN
        move = self.StockMove.search([('origin', '=', 'MY-ORIGIN-1')])
        self.assertEqual(move.procure_method, 'make_to_stock')

    def test_03_orderpoint_max_qty_perc_trigger_is_mts_no_orderpoint(self):
        # GIVEN
        self.stock_route_mto.write(
            {
                'mts_else_mto_condition': 'orderpoint_max_qty_perc',
                'orderpoint_max_qty_perc': 50.0,
            }
        )
        self.orderpoint_1.unlink()
        procurement = self.ProcurementGroup.Procurement(
            product_id=self.product_1,
            product_qty=6,
            product_uom=self.product_1.uom_id,
            # Destination location
            location_id=self.stock_location_customers,
            name=self.product_1.name,
            origin='MY-ORIGIN-1',
            company_id=self.company_main,
            values={
                'group_id': self.ProcurementGroup,
                'date_planned': '2020-02-19 00:00:00',
            },
        )
        # WHEN
        self.StockRule._run_pull([(procurement, self.stock_rule_mts_mto)])
        # THEN
        move = self.StockMove.search([('origin', '=', 'MY-ORIGIN-1')])
        self.assertEqual(move.procure_method, 'make_to_stock')

    def test_04_orderpoint_max_qty_perc_trigger_is_mts_no_mto_route(self):
        # GIVEN
        self.stock_route_mto.write(
            {
                'mts_else_mto_condition': 'orderpoint_max_qty_perc',
                'orderpoint_max_qty_perc': 50.0,
            }
        )
        self.product_1.route_ids = [(5,)]
        procurement = self.ProcurementGroup.Procurement(
            product_id=self.product_1,
            product_qty=6,
            product_uom=self.product_1.uom_id,
            # Destination location
            location_id=self.stock_location_customers,
            name=self.product_1.name,
            origin='MY-ORIGIN-1',
            company_id=self.company_main,
            values={
                'group_id': self.ProcurementGroup,
                'date_planned': '2020-02-19 00:00:00',
            },
        )
        # WHEN
        self.StockRule._run_pull([(procurement, self.stock_rule_mts_mto)])
        # THEN
        move = self.StockMove.search([('origin', '=', 'MY-ORIGIN-1')])
        self.assertEqual(move.procure_method, 'make_to_stock')
