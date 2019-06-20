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
        cls.ResPartner = cls.env['res.partner']
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
        # Wood Corner
        cls.partner_1 = cls.env.ref('base.res_partner_1')
        # Deco Addict
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        # Agrolait, Michel Fletcher
        cls.partner_address_4 = cls.env.ref('base.res_partner_address_4')
        # Gemini Furniture
        cls.partner_3 = cls.env.ref('base.res_partner_3')
        # Gemini Furniture, Edwin Hansen
        cls.partner_address_5 = cls.env.ref('base.res_partner_address_5')
        # Ready Mat.
        cls.partner_4 = cls.env.ref('base.res_partner_4')
        # Ready Mat, Kim Snyder
        cls.partner_address_13 = cls.env.ref('base.res_partner_address_13')
        cls.partner_demo = cls.env.ref('base.user_demo_res_partner')
        # Machine Groups.
        cls.machine_group_1 = cls.env.ref('machine.machine_group_1')
        cls.machine_group_2 = cls.env.ref('machine.machine_group_2')
        # CPU
        cls.cpu_xeon = cls.env.ref('machine.machine_cpu_xeon_e3113')
        # OS
        cls.os_ubuntu_1604 = cls.env.ref('machine.machine_os_ubuntu_1604')
        # DB
        cls.db_postgresql_960 = cls.env.ref(
            'machine.machine_db_postgresql_960')
