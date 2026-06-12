from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class Test3PlServiceConstraints(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TplService = cls.env['tpl.service']

    def test_01_3pl_service_filter_expression_wrong_context(self):
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Incorrect Filter Expression\. Got: .+"
        ):
            self.TplService.create(
                {
                    'name': 'MY-SERVICE-1',
                    'integration': 'my_integration_1',
                    'filter_expression': 'something.name == "abc"',
                }
            )
