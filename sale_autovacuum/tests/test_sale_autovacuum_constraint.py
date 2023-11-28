from odoo.exceptions import ValidationError

from .common import TestSaleAutovacuumCommon


class TestSaleAutovacuumConstraint(TestSaleAutovacuumCommon):
    def test_01_domain_syntactically_incorrect_bad_form(self):
        with self.assertRaises(ValidationError):
            self.sale_autovac_rule_1.domain = "{}"

    def test_02_domain_unparsable(self):
        with self.assertRaises(ValidationError):
            self.sale_autovac_rule_1.domain = "xxx"

    def test_03_domain_not_existing_field(self):
        with self.assertRaises(ValidationError):
            self.sale_autovac_rule_1.domain = "[('xxx', '=', '123')]"
