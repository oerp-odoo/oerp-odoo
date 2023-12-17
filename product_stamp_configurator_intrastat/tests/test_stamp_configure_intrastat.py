from odoo.addons.product_stamp_configurator.tests.common import (
    TestProductStampConfiguratorCommon,
)


class TestStampConfigureIntrastat(TestProductStampConfiguratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CrmLead = cls.env['crm.lead']
        cls.intrastat_code_office_desks = cls.env.ref(
            'account_intrastat.commodity_code_2018_94031051'
        )

    def test_01_stamp_configure_use_default_intrastat(self):
        # GIVEN
        self.company_main.intrastat_stamp_default_code_id = (
            self.intrastat_code_office_desks.id
        )
        cfg = self.StampConfigure.create(
            {
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'material_counter_id': self.stamp_material_plastic_05.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'quantity_mold': 1,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertEqual(cfg.intrastat_code_id, self.intrastat_code_office_desks)
        self.assertEqual(
            res['die']['product'].intrastat_code_id, self.intrastat_code_office_desks
        )
        self.assertEqual(
            res['counter_die']['product'].intrastat_code_id,
            self.intrastat_code_office_desks,
        )
        self.assertEqual(
            res['mold']['product'].intrastat_code_id, self.intrastat_code_office_desks
        )

    def test_02_stamp_configure_not_use_default_intrastat(self):
        # GIVEN
        cfg = self.StampConfigure.create(
            {
                'partner_id': self.partner_azure.id,
                'die_id': self.stamp_die_default.id,
                'design_id': self.stamp_design_f.id,
                'material_id': self.stamp_material_brass_7.id,
                'material_counter_id': self.stamp_material_plastic_05.id,
                'difficulty_id': self.stamp_difficulty_a.id,
                'size_length': 15,
                'size_width': 10,
                'quantity_dies': 10,
                'quantity_spare_dies': 3,
                'quantity_counter_dies': 10,
                'quantity_counter_spare_dies': 10,
                'quantity_mold': 1,
            }
        )
        # WHEN
        res = cfg.action_configure()
        # THEN
        self.assertFalse(cfg.intrastat_code_id)
        self.assertFalse(res['die']['product'].intrastat_code_id)
        self.assertFalse(res['counter_die']['product'].intrastat_code_id)
        self.assertFalse(res['mold']['product'].intrastat_code_id)
