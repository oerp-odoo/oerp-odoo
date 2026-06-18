from odoo.tests.common import TransactionCase

from ..const import CFG_PARAM_NO_DEFAULT_TEAM


class TestCrmNoDefaultTeam(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.CrmLead = cls.env['crm.lead']
        cls.IrConfigParameter.set_param(CFG_PARAM_NO_DEFAULT_TEAM, True)

    def test_01_create_lead_no_default_team(self):
        # WHEN
        lead = self.CrmLead.create({'name': 'MY-LEAD-1'})
        # THEN
        self.assertFalse(lead.team_id)

    def test_02_create_lead_no_default_team_disabled(self):
        # GIVEN
        self.IrConfigParameter.set_param(CFG_PARAM_NO_DEFAULT_TEAM, False)
        # WHEN
        lead = self.CrmLead.create({'name': 'MY-LEAD-1'})
        # THEN
        self.assertTrue(lead.team_id)
