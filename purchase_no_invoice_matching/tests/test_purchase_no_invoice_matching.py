from odoo.tests.common import tagged

from odoo.addons.purchase.tests.test_purchase_invoice import TestPurchaseToInvoiceCommon

from ..const import CFG_PARAM_NO_INVOICE_MATCHING


@tagged('post_install', '-at_install')
class TestPurchaseNoInvoiceMatching(TestPurchaseToInvoiceCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrConfigParameter = cls.env['ir.config_parameter']

    def test_01_invoice_match_via_po_reference_enabled(self):
        # GIVEN
        po = self.init_purchase(confirm=True, products=[self.product_order])
        invoice = self.init_invoice(
            'in_invoice', partner=self.partner_a, products=[self.product_order]
        )
        # WHEN
        invoice._find_and_set_purchase_orders(
            ['my_match_reference'], invoice.partner_id.id, invoice.amount_total
        )
        # THEN
        self.assertTrue(invoice in po.invoice_ids)
        self.assertEqual(invoice.amount_total, po.amount_total)

    def test_02_invoice_match_via_po_reference_disabled(self):
        # GIVEN
        self.IrConfigParameter.set_param(CFG_PARAM_NO_INVOICE_MATCHING, True)
        po = self.init_purchase(confirm=True, products=[self.product_order])
        invoice = self.init_invoice(
            'in_invoice', partner=self.partner_a, products=[self.product_order]
        )
        # WHEN
        invoice._find_and_set_purchase_orders(
            ['my_match_reference'], invoice.partner_id.id, invoice.amount_total
        )
        # THEN
        self.assertFalse(invoice in po.invoice_ids)
