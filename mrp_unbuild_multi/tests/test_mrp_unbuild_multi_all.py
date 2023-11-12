from odoo.exceptions import ValidationError

from .common import TestMrpUnbuildMultiCommon


class TestMrpUnbuildMultiAll(TestMrpUnbuildMultiCommon):
    def test_01_mrp_unbuild_multi_all_ok(self):
        # GIVEN
        wiz = self.MrpUnbuildMulti.with_context(
            active_ids=self.mos.ids,
            active_model='mrp.production',
        ).create(
            {
                'unbuild_type': 'all',
            }
        )
        # WHEN
        wiz.action_unbuild_multi()
        # THEN
        unbuilds = self.MrpUnbuild.search(
            [('mo_id', 'in', self.mos.ids)],
        )
        # 3 for each SN + 1 LOT + 1 untracked
        self.assertEqual(len(unbuilds), 5)
        for unbuild in unbuilds:
            self.assertEqual(
                unbuild.state, 'done', unbuild.mo_id.product_id.name
            )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S001'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S001'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S002'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S002'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S003'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S003'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'L001'),
            self.mo_tracked_lot,
            3,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: not r.lot_id),
            self.mo_untracked,
            3,
        )

    def test_02_mrp_unbuild_multi_all_partial(self):
        # GIVEN
        # Unbuild one MO
        wiz_1 = self.MrpUnbuildMulti.with_context(
            active_ids=self.mo_untracked.ids,
            active_model='mrp.production',
        ).create(
            {
                'unbuild_type': 'all',
            }
        )
        wiz_1.action_unbuild_multi()
        unbuild_init = self.MrpUnbuild.search(
            [('mo_id', '=', self.mo_untracked.id)],
        )
        # Now unbuild all mos including init one (that one should be
        # skipped).
        wiz_2 = self.MrpUnbuildMulti.with_context(
            active_ids=self.mos.ids,
            active_model='mrp.production',
        ).create(
            {
                'unbuild_type': 'all',
            }
        )
        # WHEN
        res = wiz_2.action_unbuild_multi()
        # THEN
        self.assertCountEqual(
            res['context']['mo_unbuilt_ids'],
            (self.mos - self.mo_untracked).ids,
        )
        self.assertEqual(
            res['context']['mo_skipped_ids'], self.mo_untracked.ids
        )
        self.assertEqual(len(unbuild_init), 1)
        self.assertUnbuild(unbuild_init, self.mo_untracked, 3)
        unbuilds = (
            self.MrpUnbuild.search(
                [('mo_id', 'in', self.mos.ids)],
            )
            - unbuild_init
        )
        # 3 for each SN + 1 untracked
        self.assertEqual(len(unbuilds), 4)
        for unbuild in unbuilds:
            self.assertEqual(
                unbuild.state, 'done', unbuild.mo_id.product_id.name
            )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S001'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S001'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S002'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S002'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'S003'),
            self.mos_tracked_sn.filtered(
                lambda r: r.lot_producing_id.name == 'S003'
            ),
            1,
        )
        self.assertUnbuild(
            unbuilds.filtered(lambda r: r.lot_id.name == 'L001'),
            self.mo_tracked_lot,
            3,
        )

    def test_03_mrp_unbuild_multi_all_not_done(self):
        # GIVEN
        mo_draft = self.env.ref('mrp.mrp_production_1')
        wiz = self.MrpUnbuildMulti.with_context(
            active_ids=mo_draft.ids,
            active_model='mrp.production',
        ).create(
            {
                'unbuild_type': 'all',
            }
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"To unbuild, all manufacturing orders must be in done state\."
            + r" Incorrect ones: .+",
        ):
            wiz.action_unbuild_multi()

    # TODO: Move this to separate test class!
    def test_04_unbuild_summary_defaults(self):
        # GIVEN
        mos_unbuilt = self.mo_tracked_sn | self.mo_tracked_lot
        mos_skipped = self.mo_untracked
        # WHEN
        res = self.MrpUnbuildMultiSummary.with_context(
            mo_unbuilt_ids=mos_unbuilt.ids, mo_skipped_ids=mos_skipped.ids
        ).default_get([])
        # THEN
        self.assertIn(
            self.mo_tracked_sn.name,
            res['mo_unbuilt_names'],
        )
        self.assertIn(
            self.mo_tracked_lot.name,
            res['mo_unbuilt_names'],
        )
        self.assertEqual(res['mo_skipped_names'], self.mo_untracked.name)
