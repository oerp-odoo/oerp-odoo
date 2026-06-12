from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase

from odoo.addons.delivery_3pl.utils.picking import auto_finish_picking


class TestAutoFinishPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.ResPartner = cls.env['res.partner']
        cls.StockPicking = cls.env['stock.picking']
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.product_consu_1, cls.product_stored_1 = cls.ProductProduct.create(
            [
                {'name': 'MY-CONSU-PRODUCT-1', 'type': 'consu'},
                {'name': 'MY-STORED-PRODUCT-1', 'is_storable': True},
            ]
        )

    def test_01_auto_finish_picking(self):
        # GIVEN
        picking = self.StockPicking.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product_consu_1.id,
                            "product_uom_qty": 3,
                        },
                    ),
                ],
            }
        )
        # WHEN
        auto_finish_picking(picking)
        # THEN
        self.assertEqual(picking.state, 'done')
        sml = picking.move_ids[0].move_line_ids[0]
        self.assertEqual(sml.quantity, 3)

    def test_02_auto_finish_picking_not_available(self):
        # GIVEN
        picking = self.StockPicking.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product_stored_1.id,
                            "product_uom_qty": 3,
                        },
                    ),
                ],
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(UserError, r"Transfer trouble alert"):
            auto_finish_picking(picking)
