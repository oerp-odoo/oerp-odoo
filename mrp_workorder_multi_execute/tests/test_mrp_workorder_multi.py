from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

MULTI_WORKCENTER_MSG = r"Can only execute workorders with the same workcenter!"


class TestMrpWorkorderMulti(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.MrpBom = cls.env['mrp.bom']
        cls.MrpProduction = cls.env['mrp.production']
        cls.MrpWorkorder = cls.env['mrp.workorder']
        cls.MrpWorkcenter = cls.env['mrp.workcenter']
        cls.MrpWorkcenterProductivity = cls.env['mrp.workcenter.productivity']
        # Wizard
        cls.MrpWorkorderMultiExecute = cls.env['mrp.workorder.multi.execute']
        # Wizard's service
        cls.MrpWorkorderMultiExecuteService = cls.env[
            'mrp.workorder.multi.execute.service'
        ]
        # Equipment failure
        cls.productivity_loss_failure = cls.env.ref('mrp.block_reason1')
        cls.mrp_workcenter_dig, cls.mrp_workcenter_cut = cls.MrpWorkcenter.create(
            [
                {'name': 'Digging Center'},
                {'name': 'Cutting Center'},
            ]
        )
        cls.product_1, cls.product_1_comp = cls.ProductProduct.create(
            [
                {'name': 'Product 1', 'type': 'product'},
                {'name': 'Product 1 Component', 'type': 'consu'},
            ]
        )
        cls.bom_1 = cls.MrpBom.create(
            [
                # bom_1
                {
                    "product_tmpl_id": cls.product_1.product_tmpl_id.id,
                    "product_qty": 1,
                    "bom_line_ids": [
                        (0, 0, {"product_id": cls.product_1_comp.id, "product_qty": 1}),
                    ],
                    'operation_ids': [
                        (
                            0,
                            0,
                            {
                                'name': 'OP1',
                                'workcenter_id': cls.mrp_workcenter_dig.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                'name': 'OP2',
                                'workcenter_id': cls.mrp_workcenter_cut.id,
                            },
                        ),
                    ],
                },
            ]
        )
        cls.mo_1, cls.mo_2, cls.mo_3 = cls.MrpProduction.create(
            [
                {
                    'product_id': cls.product_1.id,
                    'product_uom_id': cls.product_1.uom_id.id,
                    'product_qty': 10,
                    'bom_id': cls.bom_1.id,
                },
                {
                    'product_id': cls.product_1.id,
                    'product_uom_id': cls.product_1.uom_id.id,
                    'product_qty': 20,
                    'bom_id': cls.bom_1.id,
                },
                {
                    'product_id': cls.product_1.id,
                    'product_uom_id': cls.product_1.uom_id.id,
                    'product_qty': 30,
                    'bom_id': cls.bom_1.id,
                },
            ]
        )
        cls.mos = cls.mo_1 | cls.mo_2 | cls.mo_3
        # Strangely on standard, workorders are only created via
        # onchange trigger.. So we trigger it manually.
        cls.mos._create_workorder()
        cls.mos.action_assign()
        cls.mos.button_plan()
        cls.workorders = cls.mos.mapped('workorder_ids')
        # MO 1 WOs
        cls.mo_1_wo_dig = cls.mo_1.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_dig
        )
        cls.mo_1_wo_cut = cls.mo_1.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_cut
        )
        # MO 2 WOs
        cls.mo_2_wo_dig = cls.mo_2.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_dig
        )
        cls.mo_2_wo_cut = cls.mo_2.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_cut
        )
        # MO 3 WOs
        cls.mo_3_wo_dig = cls.mo_3.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_dig
        )
        cls.mo_3_wo_cut = cls.mo_3.workorder_ids.filtered(
            lambda r: r.workcenter_id == cls.mrp_workcenter_cut
        )
        cls.wos_dig = cls.mo_1_wo_dig | cls.mo_2_wo_dig | cls.mo_3_wo_dig

    def test_01_workorder_multi_exec_start(self):
        # WHEN
        self.MrpWorkorderMultiExecuteService.start(self.wos_dig)
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'progress')
        self.assertEqual(self.mo_2_wo_dig.state, 'progress')
        self.assertEqual(self.mo_3_wo_dig.state, 'progress')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertEqual(len(timelines), 3)
        self.assertEqual(timelines.mapped('date_end'), [False, False, False])
        # done here means in progress..
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'done')

    def test_02_workorder_multi_exec_finish(self):
        # WHEN
        self.MrpWorkorderMultiExecuteService.finish(self.wos_dig)
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'done')
        self.assertEqual(self.mo_2_wo_dig.state, 'done')
        self.assertEqual(self.mo_3_wo_dig.state, 'done')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        # Because we finished without starting it!
        self.assertFalse(timelines)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_03_workorder_multi_exec_start_finish(self):
        # GIVEN
        self.MrpWorkorderMultiExecuteService.start(self.wos_dig)
        # WHEN
        self.MrpWorkorderMultiExecuteService.finish(self.wos_dig)
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'done')
        self.assertEqual(self.mo_2_wo_dig.state, 'done')
        self.assertEqual(self.mo_3_wo_dig.state, 'done')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertEqual(len(timelines), 3)
        self.assertTrue(timelines[0].date_end)
        self.assertTrue(timelines[1].date_end)
        self.assertTrue(timelines[2].date_end)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_04_workorder_multi_exec_pause(self):
        # WHEN
        self.MrpWorkorderMultiExecuteService.pause(self.wos_dig)
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'ready')
        self.assertEqual(self.mo_2_wo_dig.state, 'ready')
        self.assertEqual(self.mo_3_wo_dig.state, 'ready')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        # Because we paused without starting it!
        self.assertFalse(timelines)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_05_workorder_multi_exec_start_pause(self):
        # GIVEN
        self.MrpWorkorderMultiExecuteService.start(self.wos_dig)
        # WHEN
        self.MrpWorkorderMultiExecuteService.pause(self.wos_dig)
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'progress')
        self.assertEqual(self.mo_2_wo_dig.state, 'progress')
        self.assertEqual(self.mo_3_wo_dig.state, 'progress')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertEqual(len(timelines), 3)
        self.assertTrue(timelines[0].date_end)
        self.assertTrue(timelines[1].date_end)
        self.assertTrue(timelines[2].date_end)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_06_workorder_multi_exec_block(self):
        # WHEN
        productivity = self.MrpWorkorderMultiExecuteService.block(
            self.wos_dig,
            self.productivity_loss_failure,
        )
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'ready')
        self.assertEqual(self.mo_2_wo_dig.state, 'ready')
        self.assertEqual(self.mo_3_wo_dig.state, 'ready')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertFalse(timelines)
        self.assertEqual(productivity.loss_id, self.productivity_loss_failure)
        self.assertFalse(productivity.description)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'blocked')

    def test_07_workorder_multi_exec_block_wiz(self):
        # GIVEN
        wiz = self.MrpWorkorderMultiExecute.with_context(
            active_ids=self.wos_dig.ids,
            active_model='mrp.workorder',
        ).create(
            {
                'action': 'block',
                'loss_id': self.productivity_loss_failure.id,
                'loss_description': 'some-loss-text',
            }
        )
        # WHEN
        wiz.action_execute()
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'ready')
        self.assertEqual(self.mo_2_wo_dig.state, 'ready')
        self.assertEqual(self.mo_3_wo_dig.state, 'ready')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertFalse(timelines)
        productivity_loss = self.MrpWorkcenterProductivity.search(
            [
                ('loss_id', '=', self.productivity_loss_failure.id),
                ('workcenter_id', '=', self.mrp_workcenter_dig.id),
            ]
        )
        self.assertEqual(productivity_loss.description, 'some-loss-text')
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'blocked')

    def test_08_workorder_multi_exec_start_block_w_description(self):
        # GIVEN
        self.MrpWorkorderMultiExecuteService.start(self.wos_dig)
        # WHEN
        productivity = self.MrpWorkorderMultiExecuteService.block(
            self.wos_dig, self.productivity_loss_failure, 'some-loss-text'
        )
        # THEN
        self.assertEqual(self.mo_1_wo_dig.state, 'progress')
        self.assertEqual(self.mo_2_wo_dig.state, 'progress')
        self.assertEqual(self.mo_3_wo_dig.state, 'progress')
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertEqual(len(timelines), 3)
        self.assertTrue(timelines[0].date_end)
        self.assertTrue(timelines[1].date_end)
        self.assertTrue(timelines[2].date_end)
        self.assertEqual(productivity.loss_id, self.productivity_loss_failure)
        self.assertEqual(productivity.description, 'some-loss-text')
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'blocked')

    def test_09_workorder_multi_exec_unblock(self):
        # WHEN, THEN
        with self.assertRaisesRegex(UserError, r"It has already been unblocked\."):
            self.MrpWorkorderMultiExecuteService.unblock(self.wos_dig)

    def test_10_workorder_multi_exec_block_unblock(self):
        # GIVEN
        self.MrpWorkorderMultiExecuteService.block(
            self.wos_dig,
            self.productivity_loss_failure,
        )
        # WHEN
        self.MrpWorkorderMultiExecuteService.unblock(self.wos_dig)
        # THEN
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertFalse(timelines)
        # Because no timelines created (workcenter is not used, so
        # block/unblock action does not do anything)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_11_workorder_multi_exec_start_block_unblock(self):
        # GIVEN
        self.MrpWorkorderMultiExecuteService.start(self.wos_dig)
        self.MrpWorkorderMultiExecuteService.block(
            self.wos_dig,
            self.productivity_loss_failure,
        )
        # WHEN
        self.MrpWorkorderMultiExecuteService.unblock(self.wos_dig)
        # THEN
        timelines = self.MrpWorkcenterProductivity.search(
            [('workorder_id', 'in', self.wos_dig.ids)]
        )
        self.assertEqual(len(timelines), 3)
        self.assertTrue(timelines[0].date_end)
        self.assertTrue(timelines[1].date_end)
        self.assertTrue(timelines[2].date_end)
        self.assertEqual(self.mrp_workcenter_dig.working_state, 'normal')

    def test_12_workorder_multi_exec_start_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecuteService.start(
                self.mo_1_wo_dig | self.mo_1_wo_cut
            )

    def test_13_workorder_multi_exec_finish_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecuteService.finish(
                self.mo_1_wo_dig | self.mo_1_wo_cut
            )

    def test_14_workorder_multi_exec_pause_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecuteService.pause(
                self.mo_1_wo_dig | self.mo_1_wo_cut
            )

    def test_15_workorder_multi_exec_block_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecuteService.block(
                self.mo_1_wo_dig | self.mo_1_wo_cut, self.productivity_loss_failure
            )

    def test_16_workorder_multi_exec_unblock_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecuteService.unblock(
                self.mo_1_wo_dig | self.mo_1_wo_cut
            )

    def test_17_workorder_multi_exec_wiz_start_mixed_workcenters(self):
        # WHEN, THEN
        with self.assertRaisesRegex(ValidationError, MULTI_WORKCENTER_MSG):
            self.MrpWorkorderMultiExecute.with_context(
                active_ids=[self.mo_1_wo_dig.id, self.mo_1_wo_cut.id],
                active_model='mrp.workorder',
            ).create({'action': 'start'})
