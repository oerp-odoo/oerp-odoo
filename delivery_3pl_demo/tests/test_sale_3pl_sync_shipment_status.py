from odoo.fields import Command
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestSale3plSyncShipmentStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.ProductProduct = cls.env['product.product']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.TplSaleOrder = cls.env['tpl.sale.order']
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.product_1 = cls.ProductProduct.create({'name': 'MY-PRODUCT-1'})
        cls.tpl_service_1 = cls.TplService.create(
            {'name': 'MY-SERVICE-1', 'integration': 'my_integration_1'}
        )
        cls.test_user_1 = new_test_user(
            cls.env,
            'my_test_user_1',
            groups='sales_team.group_sale_salesman_all_leads,stock.group_stock_user',
        )

    def test_01_sale_3pl_shipment_status_done(self):
        # GIVEN
        sale = self.SaleOrder.with_user(self.test_user_1).create(
            {
                'partner_id': self.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        picking = sale.picking_ids[0]
        # WHEN
        res = sale.with_user(self.test_user_1).action_3pl_sync_shipment_status()
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'done')
        self.assertEqual(picking.state, 'done')
        self.assertEqual(picking.carrier_tracking_ref, 'my-ref-123')

    def test_02_sale_3pl_shipment_status_not_shipped(self):
        # GIVEN
        sale = self.SaleOrder.with_user(self.test_user_1).create(
            {
                'partner_id': self.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        picking = sale.picking_ids[0]
        # WHEN
        res = self.TplSaleOrder.sync_shipment_status(
            sale.with_context(my_integration_1_not_shipped=True)
        )
        # THEN
        self.assertEqual(res, False)
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'progress')
        self.assertEqual(picking.state, 'assigned')
        self.assertEqual(picking.carrier_tracking_ref, False)

    def test_03_sale_3pl_shipment_status_done_picking_cancelled(self):
        # GIVEN
        sale = self.SaleOrder.with_user(self.test_user_1).create(
            {
                'partner_id': self.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        picking = sale.picking_ids[0]
        picking.action_cancel()
        # WHEN
        res = self.TplSaleOrder.with_user(self.test_user_1).sync_shipment_status(sale)
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'done')
        self.assertEqual(picking.state, 'cancel')

    def test_04_sale_3pl_shipment_status_done_cron(self):
        # GIVEN
        sale = self.SaleOrder.with_user(self.test_user_1).create(
            {
                'partner_id': self.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        picking = sale.picking_ids[0]
        # WHEN
        self.TplSaleOrder.cron_sync_shipment_status(sale_ids=sale.ids)
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'done')
        self.assertEqual(picking.state, 'done')

    def test_05_sale_3pl_shipment_status_no_sale_match_cron(self):
        # GIVEN
        sale = self.SaleOrder.with_user(self.test_user_1).create(
            {
                'partner_id': self.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': self.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        sale.action_confirm()
        sale.tpl_status = False
        picking = sale.picking_ids[0]
        # WHEN
        self.TplSaleOrder.cron_sync_shipment_status(sale_ids=sale.ids)
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, False)
        self.assertEqual(picking.state, 'assigned')
