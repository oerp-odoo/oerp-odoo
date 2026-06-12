from odoo.fields import Command
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestSale3plEvents(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DeliveryCarrier = cls.env['delivery.carrier']
        cls.SaleOrder = cls.env['sale.order']
        cls.ProductProduct = cls.env['product.product']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        (cls.product_1, cls.product_delivery) = cls.ProductProduct.create(
            [
                {'name': 'MY-PRODUCT-1'},
                {'name': 'MY-DELIVERY-PRODUCT'},
            ]
        )
        cls.tpl_service_1 = cls.TplService.create(
            {'name': 'MY-SERVICE-1', 'integration': 'my_integration_1'}
        )
        cls.test_user_1 = new_test_user(
            cls.env, 'my_test_user_1', groups='sales_team.group_sale_salesman_all_leads'
        )
        cls.carrier_1 = cls.DeliveryCarrier.create(
            {'name': 'MY-CARRIER-1', 'product_id': cls.product_delivery.id}
        )

    def test_01_sale_3pl_on_confirm(self):
        # GIVEN
        sale = self.SaleOrder.create(
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
        # WHEN
        sale.with_user(self.test_user_1).action_confirm()
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'progress')

    def test_02_sale_3pl_on_confirm_with_default_carrier(self):
        # GIVEN
        self.tpl_service_1.carrier_default_id = self.carrier_1.id
        sale = self.SaleOrder.create(
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
        # WHEN
        sale.with_user(self.test_user_1).action_confirm()
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'progress')

    def test_03_sale_3pl_on_confirm_not_triggered(self):
        # GIVEN
        sale = self.SaleOrder.create(
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
        sale.tpl_service_id = False
        # WHEN
        sale.with_user(self.test_user_1).action_confirm()
        # THEN
        self.assertFalse(sale.tpl_service_id)
        self.assertFalse(sale.tpl_identifier)
        self.assertFalse(sale.tpl_status)

    def test_04_sale_3pl_on_cancel(self):
        # GIVEN
        sale = self.SaleOrder.create(
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
        sale.with_user(self.test_user_1).action_confirm()
        # WHEN
        sale.action_cancel()
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, 'cancel')

    def test_05_sale_3pl_on_draft(self):
        # GIVEN
        sale = self.SaleOrder.create(
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
        sale.with_user(self.test_user_1).action_confirm()
        # WHEN
        sale.action_draft()
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)
        self.assertEqual(sale.tpl_identifier, f'{sale.name}-MY-INTEGRATION-ID')
        self.assertEqual(sale.tpl_status, False)
