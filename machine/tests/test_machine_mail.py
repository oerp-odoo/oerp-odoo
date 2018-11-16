from . import common


class TestMachineMail(common.TestMachineCommon):
    """Class to test mailing functionality related with machines."""

    def test_onchange_partner(self):
        """Set and unset partner to get contact partner."""
        self.mit_1_1.partner_id = False
        self.mit_1_1._onchange_partner_id()
        self.mit_1_1.partner_id = self.partner_1.id
        self.mit_1_1._onchange_partner_id()
        self.assertEqual(self.mit_1_1.partner_contact_id, self.partner_1)
        self.mit_1_1.partner_id = False
        self.mit_1_1._onchange_partner_id()
        self.assertFalse(self.mit_1_1.partner_contact_id)
