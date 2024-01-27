from odoo.tests.common import TransactionCase


class TestAccountSoldQtyReportCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.AccountSoldQtyReport = cls.env['account.sold.qty.report']
        cls.AccountSoldQtyReportPrint = cls.env[
            'account.sold.qty.report.print'
        ]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.ProductProduct = cls.env['product.product']
        cls.AccountJournal = cls.env['account.journal']
        # Records
        cls.company_main = cls.env.ref('base.main_company')
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_us = cls.env.ref('base.us')
        cls.country_fr = cls.env.ref('base.fr')
        cls.journal_sale_1 = cls._get_journals('sale')[0]
        (
            cls.partner_lt,
            cls.partner_us,
            cls.partner_fr,
        ) = cls.ResPartner.create(
            [
                {
                    'name': 'LT Partner',
                    'is_company': True,
                    'country_id': cls.country_lt.id,
                },
                {
                    'name': 'US Partner',
                    'is_company': True,
                    'country_id': cls.country_us.id,
                },
                {
                    'name': 'FR Partner',
                    'is_company': True,
                    'country_id': cls.country_fr.id,
                },
            ]
        )
        cls.product_glass, cls.product_bucket = cls.ProductProduct.create(
            [
                {
                    'name': 'Glass',
                    'type': 'product',
                    'default_code': 'glass',
                    'invoice_policy': 'order',
                },
                {
                    'name': 'Bucket',
                    'type': 'product',
                    'default_code': 'bucket',
                    'invoice_policy': 'order',
                },
            ]
        )
        (
            cls.invoice_lt_1,
            cls.invoice_lt_2,
            cls.invoice_us_1,
            cls.invoice_fr_1,
        ) = cls.AccountMove.create(
            [
                {
                    'partner_id': cls.partner_lt.id,
                    'move_type': 'out_invoice',
                    'invoice_date': '2021-02-01',
                    'journal_id': cls.journal_sale_1.id,
                    'invoice_line_ids': [
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_glass.id,
                                'quantity': 1,
                                'price_unit': 1,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_bucket.id,
                                'quantity': 10,
                                'price_unit': 10,
                            },
                        ),
                    ],
                },
                {
                    'partner_id': cls.partner_lt.id,
                    'move_type': 'out_invoice',
                    'invoice_date': '2021-02-02',
                    'journal_id': cls.journal_sale_1.id,
                    'invoice_line_ids': [
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_glass.id,
                                'quantity': 2,
                                'price_unit': 2,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_bucket.id,
                                'quantity': 20,
                                'price_unit': 20,
                            },
                        ),
                    ],
                },
                {
                    'partner_id': cls.partner_us.id,
                    'move_type': 'out_invoice',
                    'invoice_date': '2021-02-03',
                    'journal_id': cls.journal_sale_1.id,
                    'invoice_line_ids': [
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_glass.id,
                                'quantity': 3,
                                'price_unit': 3,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_bucket.id,
                                'quantity': 30,
                                'price_unit': 30,
                            },
                        ),
                    ],
                },
                {
                    'partner_id': cls.partner_fr.id,
                    'move_type': 'out_invoice',
                    'invoice_date': '2021-02-04',
                    'journal_id': cls.journal_sale_1.id,
                    'invoice_line_ids': [
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_glass.id,
                                'quantity': 4,
                                'price_unit': 4,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                'product_id': cls.product_bucket.id,
                                'quantity': 40,
                                'price_unit': 40,
                            },
                        ),
                    ],
                },
            ]
        )
        invoices = (
            cls.invoice_lt_1
            | cls.invoice_lt_2
            | cls.invoice_us_1
            | cls.invoice_fr_1
        )
        invoices.action_post()

    @classmethod
    def _get_journals(cls, type_):
        return cls.AccountJournal.search([('type', '=', type_)])
