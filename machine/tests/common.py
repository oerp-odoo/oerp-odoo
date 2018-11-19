from odoo.tests import common


class TestMachineCommon(common.SavepointCase):
    """Common test class for machine module test classes.

    It has common data and common methods used to test machine module
    functionality.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common data for all test classes."""
        super(TestMachineCommon, cls).setUpClass()
        # Models.
        cls.MachineInstance = cls.env['machine.instance']
        # Production machine template.
        cls.machine_template_1 = cls.env.ref(
            'machine.machine_instance_template_1')  # sync
        # Production template instances.
        cls.mit_1_1 = cls.env.ref(
            'machine.machine_instance_template_1_instance_1')  # sync
        cls.mit_1_2 = cls.env.ref(
            'machine.machine_instance_template_1_instance_2')  # sync
        cls.mit_1_3 = cls.env.ref(
            'machine.machine_instance_template_1_instance_3')  # no sync
        # Experimental machine template.
        cls.machine_template_2 = cls.env.ref(
            'machine.machine_instance_template_2')  # no sync
        # Experimental machine instance.
        cls.mit_2_1 = cls.env.ref(
            'machine.machine_instance_template_2_instance_1')  # no sync
        # ASUSTeK
        cls.partner_1 = cls.env.ref('base.res_partner_1')
        # Agrolait
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        # Agrolait, Michel Fletcher
        cls.partner_address_4 = cls.env.ref('base.res_partner_address_4')
        # China Export
        cls.partner_3 = cls.env.ref('base.res_partner_3')
        # China Export, Chao Wang
        cls.partner_address_5 = cls.env.ref('base.res_partner_address_5')
        # Delta PC.
        cls.partner_4 = cls.env.ref('base.res_partner_4')
        # Delta PC, Charlie Bernard
        cls.partner_address_13 = cls.env.ref('base.res_partner_address_13')
        cls.partner_demo = cls.env.ref('base.user_demo_res_partner')
