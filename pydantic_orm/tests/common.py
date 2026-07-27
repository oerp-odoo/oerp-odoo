from odoo.tests.common import TransactionCase


class TestApiBaseCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.company_main = cls.env.ref('base.main_company')
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_us = cls.env.ref('base.us')
