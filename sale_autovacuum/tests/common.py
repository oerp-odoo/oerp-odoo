from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestSaleAutovacuumCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleAutovacuumRule = cls.env['sale.autovacuum.rule']
        cls.ResPartner = cls.env['res.partner']
        cls.partner_1 = cls.ResPartner.create({'name': 'P1'})
        cls.field_date_order = cls.env.ref('sale.field_sale_order__date_order')
        cls.sale_autovac_rule_1 = cls.SaleAutovacuumRule.create(
            {
                'name': 'Rule 1',
                'field_date_updated_id': cls.field_date_order.id,
                'domain': f"[('partner_id', '=', {cls.partner_1.id})]",
                'state': 'in_progress',
            }
        )
        now = datetime.now()
        cls.sale_1, cls.sale_2, cls.sale_3 = cls.SaleOrder.create(
            [
                # In a past
                {
                    'partner_id': cls.partner_1.id,
                    'date_order': now - timedelta(days=180),
                },
                {
                    'partner_id': cls.partner_1.id,
                    'date_order': now - timedelta(days=150),
                },
                # In a future.
                {
                    'partner_id': cls.partner_1.id,
                    'date_order': now + timedelta(days=180),
                },
            ]
        )
