from odoo.exceptions import ValidationError

from .common import TestOdootilCommon


class TestValidateEmail(TestOdootilCommon):
    # NOTE. We must use check_deliverability=False flag, because its a bad
    # idea to send requests to remote service for unittests.
    def test_01_validate_email_ok(self):
        self.assertTrue(
            self.Odootil.validate_email(
                'email1@example.com', check_deliverability=False
            )
        )
        self.assertTrue(
            self.Odootil.validate_email('A@B.CD', check_deliverability=False)
        )

    def test_02_validate_email_not_email(self):
        with self.assertRaises(ValidationError):
            self.Odootil.validate_email('notanemail', check_deliverability=False)

    def test_03_validate_email_not_email_ignore(self):
        res = self.Odootil.with_context(
            odootil_no_email_validation=True
        ).validate_email('notanemail', check_deliverability=False)
        self.assertTrue(res)

    def test_04_validate_email_more_than_one(self):
        with self.assertRaises(ValidationError):
            self.Odootil.validate_email(
                'email1@example.com, email2@example.com', check_deliverability=False
            )

    def test_05_validate_email_incorrect_domain(self):
        with self.assertRaises(ValidationError):
            self.Odootil.validate_email('email1@example', check_deliverability=False)

    def test_06_validate_email_with_extra_data(self):
        with self.assertRaises(ValidationError):
            self.Odootil.validate_email(
                '"Name Surname" <email1@example.com>', check_deliverability=False
            )
