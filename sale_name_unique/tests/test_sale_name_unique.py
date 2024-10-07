from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..models.res_config_settings import CFG_PARAM_SALE_NAME_UNIQ


class TestSaleNameUnique(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.ResCompany = cls.env['res.company']
        cls.ResPartner = cls.env['res.partner']
        cls.SaleOrder = cls.env['sale.order']
        cls.IrConfigParameter.set_param(CFG_PARAM_SALE_NAME_UNIQ, True)
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        cls.sale_1 = cls.SaleOrder.create(
            {'partner_id': cls.partner_1.id, 'name': 'MY-SALE-ORDER-1'}
        )

    def test_01_sale_name_unique(self):
        with self.assertRaisesRegex(
            ValidationError, r"Sale Order with this number \(.+\) already exists!"
        ):
            self.SaleOrder.create(
                {'partner_id': self.partner_1.id, 'name': self.sale_1.name}
            )

    def test_02_sale_name_not_unique_different_company(self):
        # GIVEN
        company_2 = self.ResCompany.create({'name': 'MY-NEW-COMPANY-123123'})
        partner_2 = self.ResPartner.create(
            {'name': 'MY-PARTNER-2', 'company_id': company_2.id}
        )
        # WHEN, THEN
        try:
            self.SaleOrder.create(
                {
                    'partner_id': partner_2.id,
                    'name': self.sale_1.name,
                    'company_id': company_2.id,
                }
            )
        except ValidationError as e:
            self.fail(f"Sale must be created on different company. Error: {e}")

    def test_03_sale_name_unique_disabled(self):
        # GIVEN
        self.IrConfigParameter.set_param(CFG_PARAM_SALE_NAME_UNIQ, False)
        # WHEN, THEN
        try:
            self.SaleOrder.create(
                {'partner_id': self.partner_1.id, 'name': self.sale_1.name}
            )
        except ValidationError as e:
            self.fail(f"Sale must be created (name uniqueness is disabled). Error: {e}")
