from odoo.tests.common import TransactionCase


class TestPartialPrefill(TransactionCase):
    """Class to test if move lines are partially filled on confirm."""

    @classmethod
    def setUpClass(cls):
        """Set up data."""
        super().setUpClass()
        # GIVEN
        cls.picking_out_1 = cls.env.ref(
            'stock.outgoing_shipment_main_warehouse2'
        )
        cls.picking_type_delivery = cls.picking_out_1.picking_type_id
        cls.picking_type_delivery.write(
            {
                # To make sure reservation won't trigger its own logic.
                'reservation_method': 'manual',
                'show_operations': True,
                'partial_prefill_move_lines': True,
            }
        )
        cls.picking_type_delivery.partial_prefill_move_lines = True
        cls.product_lamp = cls.env.ref('product.product_delivery_02')
        cls.product_box = cls.env.ref('product.product_product_7')
        cls.product_box.tracking = 'serial'
        cls.move_lamp = cls.picking_out_1.move_lines[0]
        cls.picking_out_1.move_lines = [
            (
                0,
                0,
                {
                    'product_id': cls.product_box.id,
                    'name': cls.product_box.name,
                    'product_uom_qty': 2,
                    'product_uom': cls.product_box.uom_id.id,
                    'location_id': cls.move_lamp.location_id.id,
                    'location_dest_id': cls.move_lamp.location_dest_id.id,
                },
            )
        ]
        cls.move_box = cls.picking_out_1.move_lines - cls.move_lamp

    def test_01_partial_prefill_on_confirm_ok(self):
        """Partially prefill on confirm."""
        # WHEN
        self.picking_out_1.action_confirm()
        # THEN
        move_lines = self.picking_out_1.move_line_ids
        # 1 for lamp, 2 for Box (per serial number)
        self.assertEqual(len(move_lines), 3)
        move_line_lamp = move_lines.filtered(
            lambda r: r.product_id == self.product_lamp
        )
        # Product Lamp
        self.assertEqual(len(move_line_lamp), 1)
        self.assertEqual(move_line_lamp.move_id, self.move_lamp)
        self.assertEqual(move_line_lamp.qty_done, 45)
        self.assertEqual(move_line_lamp.product_uom_qty, 0)
        self.assertFalse(move_line_lamp.lot_id)
        # Product Box
        move_lines_box = move_lines.filtered(
            lambda r: r.product_id == self.product_box
        )
        self.assertEqual(len(move_lines_box), 2)
        move_line_box_1 = move_lines_box[0]
        self.assertEqual(move_line_box_1.move_id, self.move_box)
        self.assertEqual(move_line_box_1.qty_done, 1)
        self.assertEqual(move_line_box_1.product_uom_qty, 0)
        self.assertFalse(move_line_box_1.lot_id)
        move_line_box_2 = move_lines_box[0]
        self.assertEqual(move_line_box_2.move_id, self.move_box)
        self.assertEqual(move_line_box_2.qty_done, 1)
        self.assertEqual(move_line_box_2.product_uom_qty, 0)
        self.assertFalse(move_line_box_2.lot_id)

    def test_02_partial_prefill_on_confirm_reserve_at_confirm(self):
        """Check if partial fill is ignored on at_cofirm reserve method."""
        # WHEN
        self.picking_type_delivery.reservation_method = 'at_confirm'
        self.picking_out_1.action_confirm()
        # THEN
        # This is a bit lame check, but at_confirm can create lines
        # during reservation. Though we assume that lamp product has no
        # stock, so there won't be 3 lines..
        self.assertNotEqual(len(self.picking_out_1.move_line_ids), 3)
