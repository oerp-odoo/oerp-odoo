from odoo.tests import common


class TestMachineCommon(common.TransactionCase):
    """Common test class for machine module test classes.

    It has common data and common methods used to test machine module
    functionality.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common data for all test classes."""
        super().setUpClass()
        # Models.
        cls.MachineInstance = cls.env['machine.instance']
        cls.ResPartner = cls.env['res.partner']
        # Production instances.
        cls.machine_instance_wood = cls.env.ref('machine.machine_instance_wood')
        cls.machine_instance_deco = cls.env.ref('machine.machine_instance_deco')
        cls.machine_instance_gemini = cls.env.ref('machine.machine_instance_gemini')
        # Experimental machine instance.
        cls.machine_instance_readymat = cls.env.ref('machine.machine_instance_readymat')
        # Companies.
        cls.company_main = cls.env.ref('base.main_company')
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
        cls.partner_demo = cls.env.ref('base.user_demo').partner_id
        # Machine Groups.
        cls.machine_group_1 = cls.env.ref('machine.machine_group_1')
        cls.machine_group_2 = cls.env.ref('machine.machine_group_2')
        # CPU
        cls.cpu_xeon = cls.env.ref('machine.machine_cpu_xeon_e3113')
        # OS
        cls.os_ubuntu_1604 = cls.env.ref('machine.machine_os_ubuntu_1604')
        # DB
        cls.db_postgresql_960 = cls.env.ref('machine.machine_db_postgresql_960')
