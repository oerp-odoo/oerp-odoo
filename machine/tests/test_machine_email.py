import markupsafe

from odoo.exceptions import UserError

from . import common


def predicate_machine_instance(machine):
    return lambda r: r.machine_instance_id == machine


class TestMachineEmail(common.TestMachineCommon):
    """Class to test mailing functionality related with machines."""

    @classmethod
    def setUpClass(cls):
        """Set up custom data for machine mail tests."""
        super().setUpClass()
        cls.MailMessage = cls.env['mail.message']
        cls.MachineEmail = cls.env['machine.email']
        cls.wizard = cls.MachineEmail.create({})
        cls.base_message_domain = [
            ('model', '=', 'machine.instance'),
            ('message_type', '=', 'email'),
        ]

    def _test_recipients(self, items, wizard):
        recipients = wizard.recipient_ids
        self.assertEqual(len(items), len(recipients))
        for machine, partners in items:
            recipient = recipients.filtered(predicate_machine_instance(machine))
            target_partners = recipient.partner_ids
            self.assertEqual(
                partners,
                target_partners,
                f'Machine: {machine.name} -> Partners: '
                + f'{partners.mapped("display_name")} != '
                + f'{target_partners.mapped("display_name")}',
            )

    def test_01_onchange_machine_group_ids(self):
        """Change machine_group_ids to trigger various onchange opts."""
        # Change to have Production group selected.
        self.wizard.machine_group_ids = self.machine_group_1
        self.wizard._onchange_machine_group_ids()
        self._test_recipients(
            [
                (self.machine_instance_wood, self.ResPartner),
                (self.machine_instance_deco, self.partner_address_4),
                (self.machine_instance_gemini, self.partner_address_5),
            ],
            self.wizard,
        )
        self.wizard.machine_group_ids = self.machine_group_1 | self.machine_group_2
        self.wizard._onchange_machine_group_ids()
        self._test_recipients(
            [
                (self.machine_instance_wood, self.ResPartner),
                (self.machine_instance_deco, self.partner_address_4),
                (self.machine_instance_gemini, self.partner_address_5),
                (self.machine_instance_readymat, self.partner_address_13),
            ],
            self.wizard,
        )
        self.wizard.machine_group_ids = False
        self.wizard._onchange_machine_group_ids()
        self.assertFalse(self.wizard.recipient_ids)

    def test_02_check_recipients(self):
        """Run various cases to check if proper recipients selected."""
        # Empty recipients.
        self.assertRaises(UserError, self.wizard.check_recipients)
        # Empty email for one of recipients.
        data = [
            (
                0,
                0,
                {
                    'machine_instance_id': self.machine_instance_wood.id,
                    'partner_ids': self.ResPartner,
                },
            ),
            (
                0,
                0,
                {
                    'machine_instance_id': self.machine_instance_deco.id,
                    'partner_ids': [
                        (4, self.machine_instance_deco.partner_contact_id.id)
                    ],
                },
            ),
        ]
        self.wizard.write({'recipient_ids': data})
        self.assertRaises(UserError, self.wizard.check_recipients)
        # Recipients entered correctly.
        recipient = self.wizard.recipient_ids.filtered(lambda r: not r.partner_ids)
        recipient.partner_ids = self.partner_1
        try:
            self.wizard.check_recipients()
        except UserError:
            self.fail("Recipients were set correctly.")

    def _test_prepare_mail_message(self, vals, recipient, dest_vals):
        self.assertEqual(vals['message_type'], 'email')
        self.assertEqual(vals['model'], 'machine.instance')
        self.assertEqual(vals['res_id'], recipient.machine_instance_id.id)
        self.assertEqual(
            vals['partner_ids'],
            [(6, 0, recipient.partner_ids.ids)],
        )
        self.assertEqual(vals['subject'], dest_vals['subject'])
        self.assertEqual(
            vals['body'].striptags(),
            markupsafe.Markup(dest_vals['body']).striptags(),
        )

    def test_03_send_email(self):
        """Generate mail.message vals using general type and send it."""
        m_wood = self.machine_instance_wood
        m_deco = self.machine_instance_deco
        m_gemini = self.machine_instance_gemini
        m_readymat = self.machine_instance_readymat
        # Run message checks before generating it (for general type).
        # No subject and no body.
        self.assertRaises(UserError, self.wizard.check_message)
        # Add subject, but do not add body yet. We also add recipients,
        # because those will be used when generating messages vals.
        self.wizard.write(
            {
                'subject': 'My Subject',
                'recipient_ids': [
                    (
                        0,
                        0,
                        {
                            'machine_instance_id': m_deco.id,
                            'partner_ids': [(4, m_deco.partner_id.id)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'machine_instance_id': m_gemini.id,
                            'partner_ids': [(4, m_gemini.partner_contact_id.id)],
                        },
                    ),
                ],
            }
        )
        self.assertRaises(UserError, self.wizard.check_message)
        self.wizard.body = 'test123'
        try:
            self.wizard.check_message()
        except UserError:
            self.fail("Message data was set correctly.")
        # Generate message for each recipient (machine).
        recipients = self.wizard.recipient_ids
        dest_vals = {'subject': 'My Subject', 'body': '<p>test123</p>'}
        recipient_agrolait = recipients.filtered(
            lambda r: r.machine_instance_id == self.machine_instance_deco
        )
        vals = recipient_agrolait._prepare_mail_message()
        self._test_prepare_mail_message(vals, recipient_agrolait, dest_vals)
        recipient_china = recipients.filtered(
            lambda r: r.machine_instance_id == self.machine_instance_gemini
        )
        vals = recipient_china._prepare_mail_message()
        self._test_prepare_mail_message(vals, recipient_china, dest_vals)
        # Create messages and look for it on related machine.instance
        # records. We only create mail.message records and sending is
        # actually taken cared of by standard Odoo.
        self.wizard.action_create_mail_messages()
        # Make sure no change log is created when sending general
        # purpose email.
        self.assertFalse(
            self.MachineInstance.search_count([('change_log_ids', '!=', False)])
        )
        # Search created messages.
        search_count = self.MailMessage.search_count
        # Look for machine.instance messages where were expect no email
        # type of messages there yet.
        res = search_count(
            self.base_message_domain + [('res_id', 'in', (m_wood | m_readymat).ids)]
        )
        self.assertFalse(res)
        # Look for machine.instance messages
        res = search_count(
            self.base_message_domain + [('res_id', '=', self.machine_instance_deco.id)]
        )
        self.assertEqual(res, 1)
        res = search_count(
            self.base_message_domain
            + [('res_id', '=', self.machine_instance_gemini.id)]
        )
        self.assertEqual(res, 1)

    def _test_change_log(self, change_log, dest_tuple):
        cl = change_log
        self.assertEqual(
            (
                cl.date,
                cl.duration,
                cl.name,
                cl.priority,
                cl.user_id,
                cl.machine_instance_id,
            ),
            dest_tuple,
        )

    def test_04_send_email(self):
        """Generate mail.message vals using planned type and send it."""
        m_wood = self.machine_instance_wood
        m_deco = self.machine_instance_deco
        m_gemini = self.machine_instance_gemini
        m_readymat = self.machine_instance_readymat
        # Run message checks before generating it (for planned type).
        self.wizard.email_type = 'maintenance'
        # No date, no duration, no sub_subject, no mail_template_id.
        self.assertRaises(UserError, self.wizard.check_message)
        # Add date only.
        self.wizard.date = '2018-02-19 09:00:00'
        self.assertRaises(UserError, self.wizard.check_message)
        # Add duration.
        self.wizard.duration = 1.0
        self.assertRaises(UserError, self.wizard.check_message)
        # Add duration.
        self.wizard.sub_subject = '1.5.0'
        self.assertRaises(UserError, self.wizard.check_message)
        # Add mail_template_id (we add it via onchange, which uses
        # machine.mail_template_planned_machine_change as default one.)
        self.wizard._onchange_email_type()
        try:
            self.wizard.check_message()
        except UserError:
            self.fail("Message data was set correctly.")
        # We add recipients, because those will be used when generating
        # messages vals.
        self.wizard.write(
            {
                'recipient_ids': [
                    (
                        0,
                        0,
                        {
                            'machine_instance_id': m_deco.id,
                            'partner_ids': [(4, m_deco.partner_contact_id.id)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'machine_instance_id': m_gemini.id,
                            'partner_ids': [(4, m_gemini.partner_contact_id.id)],
                        },
                    ),
                ]
            }
        )
        # Generate message for each recipient (machine).
        recipients = self.wizard.recipient_ids
        subject_pattern = "Scheduled maintenance for {name} (1.5.0)."
        body_pattern = (
            "<p>Dear Customer, </p>"
            "<p>at 2018-02-19 09:00:00 we will do scheduled maintenance for "
            "environment you are using ({name}). </p>"
            "<p>Maintenance estimated duration is 1.0 hour(s). If you have "
            "any questions or issues with this maintenance, please reply to "
            "this email.</p>"
        )
        recipient_agrolait = recipients.filtered(
            lambda r: r.machine_instance_id == self.machine_instance_deco
        )
        vals = recipient_agrolait._prepare_mail_message()
        # Look for related change log records on respective recipient
        # records.
        self._test_change_log(
            recipient_agrolait.change_log_id,
            (
                self.wizard.date,
                self.wizard.duration,
                self.wizard.sub_subject,
                self.wizard.priority,
                self.wizard.user_id,
                self.machine_instance_deco,
            ),
        )
        # dest_vals for Agrolait machine.
        dest_vals = {
            'subject': subject_pattern.format_map(
                {'name': self.machine_instance_deco.domain}
            ),
            'body': body_pattern.format_map({'name': m_deco.domain}),
        }
        self._test_prepare_mail_message(vals, recipient_agrolait, dest_vals)
        recipient_china = recipients.filtered(
            lambda r: r.machine_instance_id == self.machine_instance_gemini
        )
        vals = recipient_china._prepare_mail_message()
        self._test_change_log(
            recipient_china.change_log_id,
            (
                self.wizard.date,
                self.wizard.duration,
                self.wizard.sub_subject,
                self.wizard.priority,
                self.wizard.user_id,
                self.machine_instance_gemini,
            ),
        )
        # dest_vals for China machine.
        dest_vals = {
            'subject': subject_pattern.format_map(
                {'name': self.machine_instance_gemini.domain}
            ),
            'body': body_pattern.format_map({'name': m_gemini.domain}),
        }
        self._test_prepare_mail_message(vals, recipient_china, dest_vals)
        # Create messages and look for it on related machine.instance
        # records. We only create mail.message records and sending is
        # actually taken cared of by standard Odoo.
        self.wizard.action_create_mail_messages()
        # Search created messages.
        search_count = self.MailMessage.search_count
        # Look for machine.instance messages where were expect no email
        # type of messages there yet.
        res = search_count(
            self.base_message_domain + [('res_id', 'in', (m_wood | m_readymat).ids)]
        )
        self.assertFalse(res)
        # Look for machine.instance messages
        res = search_count(self.base_message_domain + [('res_id', '=', m_deco.id)])
        self.assertEqual(res, 1)
        res = search_count(self.base_message_domain + [('res_id', '=', m_gemini.id)])
        self.assertEqual(res, 1)
