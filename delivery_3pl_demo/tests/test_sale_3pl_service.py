from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestSale3plService(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.ProductProduct = cls.env['product.product']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.product_1 = cls.ProductProduct.create({'name': 'MY-PRODUCT-1'})
        cls.tpl_service_1 = cls.TplService.create(
            {'name': 'MY-SERVICE-1', 'integration': 'my_integration_1'}
        )

    def test_01_sale_3pl_service(self):
        # WHEN
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
        # THEN
        self.assertEqual(sale.tpl_service_id, self.tpl_service_1)

    def test_02_sale_3pl_service_inactive(self):
        # GIVEN
        self.tpl_service_1.active = False
        # WHEN
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
        # THEN
        self.assertFalse(sale.tpl_service_id, self.tpl_service_1)
