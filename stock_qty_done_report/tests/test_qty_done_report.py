from odoo.tests.common import TransactionCase


class TestQtyDoneReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_done_1 = cls.env.ref('stock.outgoing_shipment_main_warehouse6')
        cls.picking_ready_1 = cls.env.ref('stock.incomming_shipment1')

    def test_01_get_done_qty_on_done(self):
        self.assertEqual(
            self.picking_done_1.get_qty_done_data(),
            [{'code': 'E-COM07', 'quantity': 50.0}],
        )

    def test_02_get_done_qty_on_partially_done(self):
        # GIVEN
        lines = self.picking_ready_1.move_line_ids
        line_chair = lines.filtered(lambda r: r.product_id.default_code == 'FURN_7777')
        line_lamp = lines.filtered(lambda r: r.product_id.default_code == 'FURN_8888')
        line_chair.qty_done = 10.0
        line_lamp.qty_done = 5.0
        # WHEN, THEN
        self.assertCountEqual(
            self.picking_ready_1.get_qty_done_data(),
            [
                {'code': 'FURN_7777', 'quantity': 10.0},
                {'code': 'FURN_8888', 'quantity': 5.0},
            ],
        )

    def test_03_get_done_qty_on_ready(self):
        self.assertEqual(self.picking_ready_1.get_qty_done_data(), [])

    def test_04_action_export_qty_partial_done(self):
        # GIVEN
        lines = self.picking_ready_1.move_line_ids
        line_chair = lines.filtered(lambda r: r.product_id.default_code == 'FURN_7777')
        line_lamp = lines.filtered(lambda r: r.product_id.default_code == 'FURN_8888')
        line_chair.qty_done = 10.0
        line_lamp.qty_done = 5.0
        # WHEN
        res = self.picking_ready_1.action_export_qty_done()
        # THEN
        msg = self.picking_ready_1.message_ids[0]
        name = self.picking_ready_1.name.replace('/', '')
        self.assertIn(f'Exported {name}_qty_done.csv', msg.body)
        self.assertEqual(res['type'], 'ir.actions.act_url')
