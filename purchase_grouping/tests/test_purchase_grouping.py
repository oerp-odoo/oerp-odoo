from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseGrouping(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.ProductCategory = cls.env['product.category']
        cls.ProductProduct = cls.env['product.product']
        cls.ProcurementGroup = cls.env['procurement.group']
        cls.company_main = cls.env.ref('base.main_company')
        cls.category_1 = cls.env['product.category'].create({'name': 'MY-CATEGORY-1'})
        cls.partner_vendor_1 = cls.env['res.partner'].create({'name': 'MY-PARTNER-1'})
        cls.product_1 = cls._create_product(
            'MY-PRODUCT-1', cls.category_1, cls.partner_vendor_1
        )
        cls.product_2 = cls._create_product(
            'MY-PRODUCT-2', cls.category_1, cls.partner_vendor_1
        )
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.stock_location_route = cls.env.ref('purchase_stock.route_warehouse0_buy')
        cls.stock_rule_buy = cls.stock_location_route.rule_ids[0]
        cls.values = {
            'company_id': cls.company_main,
            'date_planned': fields.Datetime.now(),
        }

    @classmethod
    def _create_product(cls, name, category, partner):
        product = cls.ProductProduct.create(
            {
                'name': name,
                'type': 'product',
                'categ_id': category.id,
                'seller_ids': [(0, 0, {'partner_id': partner.id, 'min_qty': 1.0})],
            }
        )
        return product

    def run_procurement(self, products, origin, values):
        procure_items = []
        for product in products:
            procurement = self.ProcurementGroup.Procurement(
                product,
                1,
                product.uom_id,
                self.location_stock,
                False,
                origin,
                self.env.company,
                values,
            )
            rule = self.ProcurementGroup._get_rule(
                procurement.product_id, procurement.location_id, procurement.values
            )
            procure_items.append((procurement, rule))
        self.stock_rule_buy._run_buy(procure_items)

    def test_01_purchase_no_vendor_grouping_multi_run_buy(self):
        # GIVEN
        self.company_main.purchase_grouping = 'no_grouping'
        # WHEN
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-1',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
            },
        )
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-2',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
            },
        )
        # THEN
        purchases = self.PurchaseOrder.search(
            [('partner_id', '=', self.partner_vendor_1.id)]
        )
        self.assertEqual(len(purchases), 2)

    def test_02_purchase_grouping_disabled_multi_run_buy(self):
        # GIVEN
        self.company_main.purchase_grouping = False
        # WHEN
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-1',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
            },
        )
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-2',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
            },
        )
        # THEN
        purchases = self.PurchaseOrder.search(
            [('partner_id', '=', self.partner_vendor_1.id)]
        )
        self.assertEqual(len(purchases), 1)

    def test_03_purchase_grouping_root_procure_group_same_root(self):
        # GIVEN
        self.stock_rule_buy.group_propagation_option = 'propagate'
        group_1, group_2 = self.ProcurementGroup.create(
            [{'name': 'MY-G1'}, {'name': 'MY-G2'}]
        )
        group_2.parent_root_id = group_1.id
        self.company_main.purchase_grouping = 'root_procure_group'
        # WHEN
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-1',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
                # For some reason odoo uses group_id, but it is record, not ID!
                'group_id': group_1,
            },
        )
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-2',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
                'group_id': group_2,
            },
        )
        # THEN
        purchases = self.PurchaseOrder.search(
            [('partner_id', '=', self.partner_vendor_1.id)]
        )
        self.assertEqual(len(purchases), 1)

    def test_04_purchase_grouping_root_procure_group_different_root(self):
        # GIVEN
        self.stock_rule_buy.group_propagation_option = 'propagate'
        group_1, group_2 = self.ProcurementGroup.create(
            [{'name': 'MY-G1'}, {'name': 'MY-G2'}]
        )
        self.company_main.purchase_grouping = 'root_procure_group'
        # WHEN
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-1',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
                # For some reason odoo uses group_id, but it is record, not ID!
                'group_id': group_1,
            },
        )
        self.run_procurement(
            self.product_1 | self.product_2,
            'MY-ORIGIN-2',
            {
                'company_id': self.company_main,
                'date_planned': fields.Datetime.now(),
                'group_id': group_2,
            },
        )
        # THEN
        purchases = self.PurchaseOrder.search(
            [('partner_id', '=', self.partner_vendor_1.id)]
        )
        self.assertEqual(len(purchases), 2)
