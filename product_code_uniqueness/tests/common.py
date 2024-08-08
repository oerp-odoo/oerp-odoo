from odoo.tests.common import TransactionCase

from ..models.res_config_settings import CFG_PARAM_PRODUCT_CODE_UNIQUE


class TestProductCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Set up data for product code tests."""
        super().setUpClass()
        cls.ResCompany = cls.env['res.company']
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.product_comp_rule = cls.env.ref('product.product_comp_rule')
        # Product code 'E-COM07'.
        cls.product_1 = cls.env.ref('product.product_product_6')
        # Product code 'FURN_7800'.
        cls.product_2 = cls.env.ref('product.product_product_3')
        cls.main_company_id = cls.env.ref('base.main_company').id
        cls.demo_company_id = cls.ResCompany.create({'name': "Demo Company"}).id
        # By default, product's company is not set.
        (cls.product_1 | cls.product_2).company_id = cls.main_company_id
        # By default, uniqueness is 'disabled' so we will enable it.
        cls.IrConfigParameter.set_param(CFG_PARAM_PRODUCT_CODE_UNIQUE, 'enabled')
