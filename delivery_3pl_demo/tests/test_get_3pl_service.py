from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestGet3plService(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.ProductProduct = cls.env['product.product']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.product_1 = cls.ProductProduct.create({'name': 'MY-PRODUCT-1'})
        cls.sale_1 = cls.SaleOrder.create(
            {
                'partner_id': cls.partner_1.id,
                'order_line': [
                    Command.create(
                        {
                            'product_id': cls.product_1.id,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                    )
                ],
            }
        )
        cls.tpl_service_1 = cls.TplService.create(
            {'name': 'MY-SERVICE-1', 'integration': 'my_integration_1'}
        )

    def test_01_get_3pl_service(self):
        # WHEN
        service = self.TplService.get_3pl_service(self.sale_1)
        # THEN
        self.assertEqual(service, self.tpl_service_1)

    def test_02_get_3pl_service_integration_specified(self):
        # WHEN
        service = self.TplService.get_3pl_service(
            self.sale_1, integration='my_integration_1'
        )
        # THEN
        self.assertEqual(service, self.tpl_service_1)

    def test_03_get_3pl_service_no_3pl_lines(self):
        # GIVEN
        # Custom demo sale lines filter not expecting this particular code.
        self.product_1.default_code = 'NOT-3PL'
        # WHEN
        service = self.TplService.get_3pl_service(self.sale_1, raise_not_found=False)
        # THEN
        self.assertEqual(service, self.TplService)

    def test_04_get_3pl_service_w_filter(self):
        # GIVEN
        service_1 = self.tpl_service_1
        service_1.filter_expression = 'sale.name == "something-123"'
        service_2 = self.TplService.create(
            {
                'name': 'MY-SERVICE-2',
                'integration': 'my_integration_1',
                'filter_expression': f'sale.name == "{self.sale_1.name}"',
            }
        )
        # WHEN
        service = self.TplService.get_3pl_service(self.sale_1)
        # THEN
        self.assertEqual(service, service_2)

    def test_05_get_3pl_service_w_filter_no_match(self):
        # GIVEN
        service_1 = self.tpl_service_1
        service_1.filter_expression = 'sale.name == "something-123"'
        # WHEN
        service = self.TplService.get_3pl_service(self.sale_1, raise_not_found=False)
        # THEN
        self.assertEqual(service, self.TplService)

    def test_06_get_3pl_service_no_match_raise(self):
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"No 3PL service found for sale order .+\. Make sure it is created "
            + r"and active\.",
        ):
            self.TplService.get_3pl_service(self.sale_1, integration='unknown')

    def test_07_get_3pl_service_inactive(self):
        # GIVNE
        self.tpl_service_1.active = False
        # WHEN
        service = self.TplService.get_3pl_service(self.sale_1, raise_not_found=False)
        # THEN
        self.assertEqual(service, self.TplService)
