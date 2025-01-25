from datetime import datetime
from unittest.mock import patch

from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleComponentAvailability(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.StockMove = cls.env['stock.move']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.ProductProduct = cls.env['product.product']
        cls.MrpProduction = cls.env['mrp.production']
        cls.MrpBom = cls.env['mrp.bom']
        (
            cls.product_1,
            cls.product_2,
            cls.product_comp_1,
            cls.product_comp_2,
        ) = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1', 'type': 'product'},
                {'name': 'MY-PRODUCT-2', 'type': 'product'},
                {'name': 'MY-COMP-PRODUCT-1', 'type': 'product'},
                {'name': 'MY-COMP-PRODUCT-2', 'type': 'product'},
            ]
        )
        cls.bom_1, cls.bom_2 = cls.MrpBom.create(
            [
                {
                    'product_tmpl_id': cls.product_1.product_tmpl_id.id,
                    'bom_line_ids': [
                        Command.create(
                            {
                                'product_id': cls.product_comp_1.id,
                                'product_uom_id': cls.product_comp_1.uom_id.id,
                                'product_qty': 1,
                            }
                        )
                    ],
                },
                {
                    'product_tmpl_id': cls.product_2.product_tmpl_id.id,
                    'bom_line_ids': [
                        Command.create(
                            {
                                'product_id': cls.product_comp_2.id,
                                'product_uom_id': cls.product_comp_2.uom_id.id,
                                'product_qty': 1,
                            }
                        )
                    ],
                },
            ]
        )
        cls.partner_customer = cls.ResPartner.create({'name': 'MY-CUSTOMER-1'})
        cls.procurement_group_1 = cls.ProcurementGroup.create(
            {'name': 'MY-PROCUREMENT-GROUP-1'}
        )
        cls.sale_1 = cls.SaleOrder.create(
            {
                'partner_id': cls.partner_customer.id,
            }
        )
        cls.sale_1_line_1, cls.sale_1_line_2 = cls.SaleOrderLine.create(
            [
                {
                    'order_id': cls.sale_1.id,
                    'product_id': cls.product_1.id,
                    'price_unit': 10,
                    'product_uom_qty': 10,
                },
                {
                    'order_id': cls.sale_1.id,
                    'product_id': cls.product_2.id,
                    'price_unit': 20,
                    'product_uom_qty': 20,
                },
            ]
        )
        cls.sale_1.procurement_group_id = cls.procurement_group_1.id
        cls.procurement_group_1.sale_id = cls.sale_1.id

    def test_01_component_avail_no_mos(self):
        self.assertEqual(self.sale_1.component_progress, 0)
        self.assertEqual(self.sale_1.component_availability_state, False)

    def test_02_component_avail_all_finished(self):
        # GIVEN
        mo = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # WHEN
        mo.state = 'done'
        # THEN
        self.assertEqual(self.sale_1.component_progress, 100)
        self.assertEqual(self.sale_1.component_availability_state, 'available')

    def test_03_component_avail_all_available(self):
        # WHEN
        mos = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        # If no components are used, then it means its always available!
        mos.mapped('move_raw_ids').unlink()
        # WHEN
        mos.action_confirm()
        # THEN
        self.assertEqual(self.sale_1.component_progress, 100)
        self.assertEqual(self.sale_1.component_availability_state, 'available')

    def test_04_component_avail_half_available_before_start(self):
        # WHEN
        mo_1, mo_2 = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        (mo_1 | mo_2).write({'date_start': datetime(2022, 2, 19)})
        mo_1.move_raw_ids.unlink()
        (mo_1 | mo_2).action_confirm()
        # WHEN
        with patch.object(
            type(self.StockMove), '_get_forecast_availability_outgoing'
        ) as m:
            raw_move = mo_2.move_raw_ids[0]
            m.return_value = {raw_move: (100, datetime(2022, 2, 18))}
            self.sale_1._compute_component_availability()
        # THEN
        self.assertEqual(self.sale_1.component_progress, 50)
        self.assertEqual(self.sale_1.component_availability_state, 'expected')

    def test_05_component_avail_half_available_after_start(self):
        # WHEN
        mo_1, mo_2 = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        (mo_1 | mo_2).write({'date_start': datetime(2022, 2, 19)})
        mo_1.move_raw_ids.unlink()
        (mo_1 | mo_2).action_confirm()
        # WHEN
        with patch.object(
            type(self.StockMove), '_get_forecast_availability_outgoing'
        ) as m:
            raw_move = mo_2.move_raw_ids[0]
            m.return_value = {raw_move: (100, datetime(2022, 2, 20))}
            self.sale_1._compute_component_availability()
        # THEN
        self.assertEqual(self.sale_1.component_progress, 50)
        self.assertEqual(self.sale_1.component_availability_state, 'late')

    def test_06_component_avail_unavailable(self):
        # WHEN
        mo_1, mo_2 = self.MrpProduction.create(
            [
                {
                    'product_id': self.product_1.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
                {
                    'product_id': self.product_2.id,
                    'product_qty': 1,
                    'procurement_group_id': self.procurement_group_1.id,
                },
            ],
        )
        (mo_1 | mo_2).write({'date_start': datetime(2022, 2, 19)})
        mo_1.move_raw_ids.unlink()
        # WHEN
        (mo_1 | mo_2).action_confirm()
        # THEN
        self.assertEqual(self.sale_1.component_progress, 50)
        self.assertEqual(self.sale_1.component_availability_state, 'unavailable')
