from odoo.tests.common import TransactionCase


class TestGenerateEmail(TransactionCase):
    """Test class for testing emails generation with qweb_view."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up data for email generation tests."""
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']
        cls.IrUiView = cls.env['ir.ui.view']
        cls.IrModelData = cls.env['ir.model.data']
        cls.MailTemplate = cls.env['mail.template']
        cls.model_res_partner = cls.env.ref('base.model_res_partner')
        cls.ir_ui_view_qweb_1 = cls.IrUiView.create(
            {
                'name': 'MY-QWEB-1',
                'type': 'qweb',
                'mode': 'primary',
                'arch_db': """
<t t-name="my_tname_1">
        <p>Dear <t t-out="object.name or ''">Mitchell Admin,</t></p>
        <p>Welcome joining us!</p>
</t>""",
            }
        )
        # to have xml_id set on ir_ui_view_qweb_1
        cls.IrModelData.create(
            {
                'module': '__export__',
                'name': 'my_qweb_1',
                'res_id': cls.ir_ui_view_qweb_1.id,
                'model': 'ir.ui.view',
            }
        )
        cls.partner_1 = cls.ResPartner.create({'name': 'MY-PARTNER-1'})
        # cls.partner_azure_brandon = cls.env.ref('base.res_partner_address_15')
        # cls.partner_azure_brandon_id = cls.partner_azure_brandon.id
        # cls.mail_template_partner_welcome = cls.env.ref(
        #     'mail_template_qweb_view.mail_template_partner_welcome'
        # )
        cls.mail_template_partner_welcome = cls.MailTemplate.create(
            {
                'name': 'Partner: Welcome',
                'model_id': cls.model_res_partner.id,
                'subject': 'Welcome Dear Customer',
                'email_from': (
                    "{{ object.company_id.partner_id.email_formatted or"
                    + " 'test@example.com' }}"
                ),
                'view_body_qweb_id': cls.ir_ui_view_qweb_1.id,
                'email_to': "{{ object.email_formatted }}",
                'body_html': """
<p>Dear
    <t
        t-out=\"object.name or ''\"
        data-oe-t-inline=\"true\"
        contenteditable=\"false\"
    >
        Mitchell Admin,
    </t>
</p>
<p>Welcome being part of us.</p>
""",
            }
        )

    def test_01_generate_email_qweb_engine(self):
        """Generate email using html_body default `qweb` engine."""
        # WHEN
        mail = self.mail_template_partner_welcome.send_mail_batch([self.partner_1.id])
        # THEN
        self.assertIn('Welcome being part of us', mail.body_html)
        self.assertEqual(str(mail.subject), 'Welcome Dear Customer')

    def test_02_generate_email_qweb_view_engine(self):
        # GIVEN
        self.mail_template_partner_welcome.body_engine = 'qweb_view'
        # WHEN
        mail = self.mail_template_partner_welcome.send_mail_batch([self.partner_1.id])
        # THEN
        self.assertIn('Welcome joining us!', mail.body_html)
        self.assertEqual(str(mail.subject), 'Welcome Dear Customer')
