from ..tools.email import is_email_in_domains
from .common import TestOdootilCommon


class TestEmailUtils(TestOdootilCommon):
    def test_01_is_email_in_domains_match(self):
        self.assertTrue(
            is_email_in_domains('john.doe@example.com', ['example.com', 'test.com'])
        )

    def test_02_is_email_in_domains_no_match(self):
        self.assertFalse(
            is_email_in_domains('john.doe@abc.com', ['example.com', 'test.com'])
        )
