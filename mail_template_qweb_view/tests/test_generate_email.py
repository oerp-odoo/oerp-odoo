from odoo.tests.common import TransactionCase


class TestGenerateEmail(TransactionCase):
    """Test class for testing emails generation with qweb_view."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up data for email generation tests."""
        super().setUpClass()
        cls.partner_azure_brandon = cls.env.ref('base.res_partner_address_15')
        cls.partner_azure_brandon_id = cls.partner_azure_brandon.id
        cls.mail_template_partner_welcome = cls.env.ref(
            'mail_template_qweb_view.mail_template_partner_welcome'
        )

    def test_01_generate_email(self):
        """Generate email using html_body default `qweb` engine."""
        res = self.mail_template_partner_welcome.generate_email(
            [self.partner_azure_brandon_id],
            ['subject', 'body_html']
        )
        body_html = res[self.partner_azure_brandon_id]['body_html']
        expected_body_html = (
            "<p>Dear\n                Brandon Freeman\n"
            "            </p>\n            <p>Welcome being part of us."
            "</p>\n        "
        )
        self.assertEqual(str(body_html), expected_body_html)
        subject = res[self.partner_azure_brandon_id]['subject']
        self.assertEqual(str(subject), 'Welcome Dear Customer')

    def test_02_generate_email(self):
        """Generate email using html_body `qweb_view` engine."""
        self.mail_template_partner_welcome.body_engine = 'qweb_view'
        res = self.mail_template_partner_welcome.generate_email(
            [self.partner_azure_brandon_id],
            ['subject', 'body_html']
        )
        body_html = res[self.partner_azure_brandon_id]['body_html']
        expected_body_html = (
            "<p>Dear Brandon Freeman</p>\n        <p>Welcome joining us!</p>"
        )
        self.assertEqual(str(body_html), expected_body_html)
        subject = res[self.partner_azure_brandon_id]['subject']
        self.assertEqual(str(subject), 'Welcome Dear Customer')
