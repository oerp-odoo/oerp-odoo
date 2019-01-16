from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from .. models.machine_instance import PRIORITY


class MachineEmail(models.TransientModel):
    """Wizard to send emails for machine contacts."""

    _name = 'machine.email'
    _description = 'Send Emails to Machine Contacts'

    machine_group_ids = fields.Many2many(
        'machine.group', string="Machine Groups")
    recipient_ids = fields.One2many(
        'machine.email.recipient', 'machine_email_id', "Recipients")
    email_type = fields.Selection(
        [('general', 'General'), ('scheduled', 'Scheduled')],
        default='general',
        required=True)
    mail_template_id = fields.Many2one(
        'mail.template',
        "Mail Template",
        domain=[('model_id.model', '=', 'machine.instance.change_log')])
    # Fields uses when creating change log record.
    user_id = fields.Many2one('res.users', "Responsible")
    priority = fields.Selection(
        PRIORITY,
        default=2)
    subject = fields.Char()
    # Used as a variable on planned email_type, where it can be used
    # to specify version or some details regarding that schedule.
    sub_subject = fields.Char()
    body = fields.Html(
        "Contents", default='', sanitize_style=True, strip_classes=True)
    date = fields.Datetime(default=fields.Datetime.now)
    duration = fields.Float(default=1.0, help="In Hours")

    @api.one
    def check_recipients(self):
        """Check recipients' correctness."""
        if not self.recipient_ids:
            raise UserError(_("At least one recipient must be specified."))
        for recipient in self.recipient_ids:
            if not recipient.partner_ids:
                raise UserError(
                    _("%s Machine recipient is missing Partners set.") %
                    recipient.machine_instance_id.name)

    @api.one
    def check_message(self):
        """Check fields for message."""
        def check(fld_key):
            if not self[fld_key]:
                string = self._fields[fld_key].string
                raise UserError(
                    _("%s field required to send an email.") % string)
        if self.email_type == 'general':
            check('subject')
            check('body')
        elif self.email_type == 'scheduled':
            check('date')
            check('duration')
            check('priority')
            check('sub_subject')
            check('mail_template_id')

    @api.onchange('machine_group_ids')
    def _onchange_machine_group_ids(self):
        # If machine_group_ids were changed, we always clear existing
        # recipients if there were any, because otherwise we would need
        # to track current set machine groups and current recipients.
        self.update({'recipient_ids': [(5, False, False)]})
        data = []
        for group in self.machine_group_ids:
            for machine in group.machine_instance_ids:
                partner_ids = machine.message_get_default_recipients()[
                    machine.id]['partner_ids']
                data.append((
                    0, 0,
                    {
                        'machine_instance_id': machine.id,
                        'partner_ids': partner_ids,
                    }
                ))
        if data:
            self.update({'recipient_ids': data})

    @api.onchange('email_type')
    def _onchange_email_type(self):
        if self.email_type == 'scheduled':
            self.mail_template_id = self.env.ref(
                'machine.mail_template_planned_machine_change').id
        else:
            self.mail_template_id = False

    @api.multi
    def action_create_mail_messages(self):
        """Create mail messages with a type email for each machine.

        Returns messages that were created.
        """
        self.check_recipients()
        self.check_message()
        messages = self.env['mail.message']
        for recipient in self.recipient_ids:
            messages |= recipient._create_mail_message()
        return messages


class MachineEmailRecipient(models.TransientModel):
    """Model to hold recipient data for MachineEmail wizard."""

    _name = 'machine.email.recipient'
    _description = 'Machine Email Recipient'
    _rec_name = 'machine_instance_id'

    machine_instance_id = fields.Many2one(
        'machine.instance',
        "Machine Instance",
        domain=[('parent_id', '!=', False)],
        required=True)
    partner_ids = fields.Many2many(
        'res.partner',
        string="Partners",
        help="Partners that will receive this email")
    machine_email_id = fields.Many2one(
        'machine.email', "Machine Email", required=True, ondelete='cascade')
    # Technical field used for mail template rendering.
    change_log_id = fields.Many2one(
        'machine.instance.change_log', "Change Log")

    def _add_change_log(self):
        """Create change log record and relate with recipient."""
        wiz = self.machine_email_id
        change_log = self.env['machine.instance.change_log'].create({
            'name': wiz.sub_subject,
            'date': wiz.date,
            'duration': wiz.duration,
            'user_id': wiz.user_id.id,
            'priority': wiz.priority,
            'machine_instance_id': self.machine_instance_id.id,

        })
        self.change_log_id = change_log.id

    def _get_subject_and_body(self):
        self.ensure_one()
        wiz = self.machine_email_id
        if wiz.email_type == 'general':
            return wiz.subject, wiz.body
        elif wiz.email_type == 'scheduled':
            # Add change log, so we can render template from it.
            self._add_change_log()
            change_log_id = self.change_log_id.id
            res = wiz.mail_template_id.generate_email(change_log_id)
            return res['subject'], res['body_html']
        else:
            raise ValidationError(
                _("Programming error: %s email_type does not exist"))

    def _prepare_mail_message(self):
        self.ensure_one()
        wiz = self.machine_email_id
        vals = {
            'message_type': 'email',
            'model': 'machine.instance',
            'res_id': self.machine_instance_id.id,
            'partner_ids': [(6, 0, self.partner_ids.ids)],
            'subject': wiz.subject,
            'body': wiz.body,
        }
        subject, body = self._get_subject_and_body()
        vals.update(subject=subject, body=body)
        return vals

    def _create_mail_message(self):
        self.ensure_one()
        vals = self._prepare_mail_message()
        return self.env['mail.message'].create(vals)
