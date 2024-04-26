from odoo.osv import expression
from odoo.tests.common import TransactionCase


class TestStockMoveOperationReportCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.StockPMoveOperationReport = cls.env['stock.move.operation.report']
        cls.AccountPaymentRegister = cls.env['account.payment.register']
        cls.AccountJournal = cls.env['account.journal']
        cls.AccountMove = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.ProductProduct = cls.env['product.product']
        cls.StockLocation = cls.env['stock.location']
        # Records
        cls.company_main = cls.env.ref('base.main_company')
        cls.warehouse_1 = cls.env.ref('stock.warehouse0')
        cls.stock_location_virtual_view = cls.env.ref(
            'stock.stock_location_locations_virtual'
        )
        cls.stock_location_stock = cls.env.ref('stock.stock_location_stock')
        cls.stock_location_customers = cls.env.ref('stock.stock_location_customers')
        cls.stock_location_suppliers = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location_suppliers = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location_production = cls.get_stock_location_by_usage('production')
        cls.stock_location_scrap = cls.get_stock_location_by_usage(
            'inventory', extra_domain=[('scrap_location', '=', True)]
        )
        cls.stock_location_transit = cls.StockLocation.create(
            {
                'name': 'Transit Location',
                'usage': 'transit',
                'location_id': cls.stock_location_virtual_view.id,
            }
        )
        cls.pricelist_1 = cls.env.ref('product.list0')
        cls.journal_bank_1 = cls._get_journals('bank')[0]
        cls.payment_method_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.country_us = cls.env.ref('base.us')
        cls.partner_azure = cls.env.ref("base.res_partner_12")
        cls.partner_azure_brandon = cls.env.ref("base.res_partner_address_15")
        cls.partner_individual = cls.ResPartner.create({'name': 'John Doe'})
        cls.product_glass, cls.product_bucket = cls.ProductProduct.create(
            [
                {
                    'name': 'Glass',
                    'type': 'product',
                    'default_code': 'glass',
                },
                {
                    'name': 'Bucket',
                    'type': 'product',
                    'default_code': 'bucket',
                },
            ]
        )

    @classmethod
    def get_stock_location_by_usage(
        cls, usage, company_id=None, limit=1, extra_domain=None
    ):
        if company_id is None:
            company_id = cls.company_main.id
        domain = [
            ('usage', '=', usage),
            ('company_id', '=', company_id),
        ]
        if extra_domain is not None:
            domain = expression.AND([domain, extra_domain])
        return cls.StockLocation.search(domain, limit=limit)

    @classmethod
    def _get_journals(cls, type_):
        return cls.AccountJournal.search([('type', '=', type_)])

    def make_stock_move(
        self,
        product,
        qty,
        location_src,
        location_dest,
        price_unit=None,
        lines=None,
        dt=None,
    ):
        if lines is None:
            lines = []
        move_vals = {
            "name": "Move Test",
            "product_id": product.id,
            "product_uom": product.uom_id.id,
            "location_id": location_src.id,
            "location_dest_id": location_dest.id,
            "product_uom_qty": qty,
        }
        if price_unit is not None:
            move_vals["price_unit"] = price_unit
        move = self.env["stock.move"].create(move_vals)
        move._action_confirm()
        move._action_assign()
        lines_data = []
        for qty_done, lot_id in lines:
            ml_vals = {
                "qty_done": qty_done,
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
            }
            if lot_id:
                ml_vals["lot_id"] = lot_id
            lines_data.append((0, 0, ml_vals))
        if lines_data:
            move.move_line_ids = lines_data
            move._action_done()
        if dt is not None:
            move.date = dt
        return move
