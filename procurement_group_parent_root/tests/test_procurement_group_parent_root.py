from odoo.addons.base.tests.common import BaseCommon


class TestProcurementGroupParentRoot(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.StockMove = cls.env['stock.move']
        cls.ProductProduct = cls.env['product.product']
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_customers = cls.env.ref('stock.stock_location_customers')
        cls.product_1, cls.product_2 = cls.ProductProduct.create(
            [
                {'name': 'MY-P1'},
                {'name': 'MY-P2'},
            ]
        )
        cls.stock_move_1, cls.stock_move_2 = cls.StockMove.create(
            [
                {
                    'name': cls.product_1.name,
                    'product_id': cls.product_1.id,
                    'product_uom_qty': 10,
                    'product_uom': cls.product_1.uom_id.id,
                    'location_id': cls.location_stock.id,
                    'location_dest_id': cls.location_customers.id,
                    'state': 'waiting',
                    'procure_method': 'make_to_order',
                },
                {
                    'name': cls.product_2.name,
                    'product_id': cls.product_2.id,
                    'product_uom_qty': 10,
                    'product_uom': cls.product_2.uom_id.id,
                    'location_id': cls.location_stock.id,
                    'location_dest_id': cls.location_customers.id,
                    'state': 'waiting',
                    'procure_method': 'make_to_order',
                },
            ]
        )

    def test_01_procurement_group_parent_root_single_group(self):
        # GIVEN
        group = self.ProcurementGroup.create({'name': 'MY-PG1'})
        # WHEN
        self.stock_move_1.group_id = group.id
        # THEN
        self.assertEqual(group.parent_root_id, group)

    def test_02_procurement_group_parent_root_multi_groups_hierarchy(self):
        # GIVEN
        group_1, group_2 = self.ProcurementGroup.create(
            [{'name': 'MY-PG1'}, {'name': 'MY-PG2'}]
        )
        # WHEN
        self.stock_move_1.group_id = group_1.id
        self.stock_move_2.write(
            {'group_id': group_2.id, 'move_dest_ids': [(6, 0, self.stock_move_1.ids)]}
        )
        # THEN
        self.assertEqual(group_1.parent_root_id, group_1)
        self.assertEqual(group_2.parent_root_id, group_1)

    def test_03_procurement_group_parent_root_multi_groups_no_hierarchy(self):
        # GIVEN
        group_1, group_2 = self.ProcurementGroup.create(
            [{'name': 'MY-PG1'}, {'name': 'MY-PG2'}]
        )
        # WHEN
        self.stock_move_1.group_id = group_1.id
        self.stock_move_2.group_id = group_2.id
        # THEN
        self.assertEqual(group_1.parent_root_id, group_1)
        self.assertEqual(group_2.parent_root_id, group_2)
