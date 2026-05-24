from odoo.tests.common import TransactionCase


class TestSale3plWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockWarehouse = cls.env['stock.warehouse']
        cls.SaleOrder = cls.env['sale.order']
        cls.ResPartner = cls.env['res.partner']
        cls.TplService = cls.env['tpl.service']
        cls.warehouse_1 = cls.env.ref('stock.warehouse0')
        cls.warehouse_2 = cls.StockWarehouse.create({'name': 'MY-WH-2', 'code': 'MWH2'})
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.tpl_service_1 = cls.TplService.create({'integration': 'my_integration_1'})
        cls.sale_1 = cls.SaleOrder.create(
            {
                'partner_id': cls.partner_1.id,
            }
        )

    def test_01_sale_3pl_warehouse(self):
        # GIVEN
        self.tpl_service_1.warehouse_id = self.warehouse_2.id
        # WHEN
        sale = self.SaleOrder.create(
            {
                'partner_id': self.partner_1.id,
            }
        )
        # THEN
        self.assertEqual(sale.warehouse_id, self.warehouse_2)

    def test_02_sale_3pl_warehouse_not_specified(self):
        # GIVEN
        self.tpl_service_1.warehouse_id = False
        # WHEN
        sale = self.SaleOrder.create(
            {
                'partner_id': self.partner_1.id,
            }
        )
        # THEN
        # Should set default one.
        self.assertEqual(sale.warehouse_id, self.warehouse_1)
