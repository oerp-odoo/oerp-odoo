from odoo.tests.common import TransactionCase, Form


class TestMrpUnbuildMultiCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.StockProductionLot = cls.env['stock.production.lot']
        cls.MrpProduction = cls.env['mrp.production']
        cls.StockAssignSerial = cls.env['stock.assign.serial']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpUnbuild = cls.env['mrp.unbuild']
        cls.MrpUnbuildMulti = cls.env['mrp.unbuild.multi']
        cls.MrpUnbuildMultiSummary = cls.env['mrp.unbuild.multi.summary']
        cls.company_main = cls.env.ref('base.main_company')
        # Products
        cls.product_consumable = cls.ProductProduct.create(
            {
                'name': 'Product Consumable',
                'detailed_type': 'consu',
            }
        )
        (
            cls.product_tracked_sn,
            cls.product_tracked_lot,
            cls.product_untracked,
        ) = cls.ProductProduct.create(
            [
                {
                    'name': 'Product Tracked by SN',
                    'detailed_type': 'product',
                    'tracking': 'serial',
                },
                {
                    'name': 'Product Tracked by Lot',
                    'detailed_type': 'product',
                    'tracking': 'lot',
                },
                {
                    'name': 'Product Untracked',
                    'detailed_type': 'product',
                    'tracking': 'none',
                },
            ]
        )
        # Lots.
        cls.production_lot_1 = cls.StockProductionLot.create(
            {
                'name': 'L001',
                'product_id': cls.product_tracked_lot.id,
                'company_id': cls.company_main.id,
            }
        )
        # BOMs
        bom_line_data = [
            (
                0,
                0,
                {
                    'product_id': cls.product_consumable.id,
                    'product_qty': 1,
                },
            )
        ]
        (
            cls.bom_tracked_sn,
            cls.bom_tracked_lot,
            cls.bom_untracked,
        ) = cls.MrpBom.create(
            [
                {
                    'product_tmpl_id': (
                        cls.product_tracked_sn.product_tmpl_id.id
                    ),
                    'product_qty': 1,
                    'bom_line_ids': bom_line_data,
                },
                {
                    'product_tmpl_id': (
                        cls.product_tracked_lot.product_tmpl_id.id
                    ),
                    'product_qty': 1,
                    'bom_line_ids': bom_line_data,
                },
                {
                    'product_tmpl_id': (
                        cls.product_untracked.product_tmpl_id.id
                    ),
                    'product_qty': 1,
                    'bom_line_ids': bom_line_data,
                },
            ]
        )
        # MOs
        cls.mo_tracked_sn = cls.create_mo(
            cls.product_tracked_sn,
            cls.bom_tracked_sn,
            3,
        )
        cls.mo_tracked_lot = cls.create_mo(
            cls.product_tracked_lot,
            cls.bom_tracked_lot,
            3,
        )
        cls.mo_untracked = cls.create_mo(
            cls.product_untracked,
            cls.bom_untracked,
            3,
        )
        # Finish MOs.
        # Handle MO tracked by SN
        (
            cls.mo_tracked_sn | cls.mo_tracked_lot | cls.mo_untracked
        ).action_confirm()
        mass_produce_ctx = (
            cls.mo_tracked_sn.action_serial_mass_produce_wizard()['context']
        )
        mass_produce_ctx.update(
            {
                'default_next_serial_number': 'S001',
                'default_serial_numbers': 'S001\nS002\nS003',
            }
        )
        stock_assign_wiz = cls.StockAssignSerial.with_context(
            **mass_produce_ctx
        ).create({})
        stock_assign_wiz.apply()
        # Handle MO tracked by Lot
        cls.mo_tracked_lot.write(
            {
                'qty_producing': 3,
                'lot_producing_id': cls.production_lot_1.id,
            }
        )
        cls.mo_untracked.qty_producing = 3
        # Tracked by SN MO split into three each having single SN.
        cls.mos_tracked_sn = (
            cls.mo_tracked_sn.procurement_group_id.mrp_production_ids
        )
        cls.mos = cls.mos_tracked_sn | cls.mo_tracked_lot | cls.mo_untracked
        # Make all MOs DONE.
        cls.force_done_raw_moves(cls.mos)
        cls.mos.button_mark_done()

    @classmethod
    def create_mo(cls, product, bom, qty_final):
        mo_form = Form(cls.MrpProduction)
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty_final
        mo = mo_form.save()
        mo.action_confirm()
        return mo

    @classmethod
    def force_done_raw_moves(cls, mos):
        for mo in mos:
            for move in mo.move_raw_ids:
                move.quantity_done = move.product_uom_qty

    def assertUnbuild(self, unbuild, mo, quantity):
        self.assertEqual(unbuild.mo_id, mo)
        self.assertEqual(unbuild.product_id, mo.product_id)
        self.assertEqual(unbuild.product_qty, quantity)
        self.assertEqual(unbuild.lot_id.name, mo.lot_producing_id.name)
