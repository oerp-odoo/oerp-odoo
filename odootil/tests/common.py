import time
from datetime import timedelta
from email.message import EmailMessage

from psycopg2.extensions import AsIs

from odoo.exceptions import AccessError
from odoo.fields import Datetime
from odoo.models import BaseModel
from odoo.tests import common
from odoo.tools import convert_file, file_path
from odoo.tools.mail import generate_tracking_message_id
from odoo.tools.misc import mute_logger

from ..tools.decor import deprecated

MODELS_PATH = 'odoo.models'
BASE_MODELS_PATH = 'odoo.addons.base.models.ir_model'
BASE_RULE_PATH = 'odoo.addons.base.models.ir_rule'
# Note. This path exists only if module base_fields_access is installed.
BASE_FIELDS_MODELS_PATH = 'odoo.addons.base_fields_access.models.ir_model_fields_rule'
SQL_DB_PATH = 'odoo.sql_db'
ODOOTIL_DECOR_PATH = 'odoo.addons.odootil.tools.decor'

DISABLED_MAIL_CONTEXT = {
    'tracking_disable': True,
    'mail_create_nolog': True,
    'mail_create_nosubscribe': True,
    'mail_notrack': True,
    'no_reset_password': True,
}
ENABLED_MAIL_CONTEXT = {
    'tracking_disable': False,
    'mail_create_nolog': False,
    'mail_create_nosubscribe': False,
    'mail_notrack': False,
    'no_reset_password': False,
}


def update_create_date(records, dt):
    table = records._table
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    records.env.cr.execute(
        """
        UPDATE %s
        SET create_date = %s
        WHERE id in %s
        """,
        (AsIs(table), dt_str, tuple(records.ids)),
    )


def _wrap_empty_iterable(objects):
    """Wrap empty iterable, so it would be iterated at least once."""
    if not objects:
        return [objects]
    return objects


def _wrap_recordset(objects):
    if isinstance(objects, BaseModel):
        return [objects]
    return objects


def switch_record_currency(self, record, mode='over_limit', currency_fld='currency_id'):
    """Change record (or related one) currency to other than company's.

    Depending on modules installed, main company currency could be
    different.
    """

    def set_rate(curr, rate):
        # Remove currency rate with dynamic date to avoid errors in
        # tests. Tests are based on the 'base.rateUSD' currency
        # rate.
        try:
            self.env.ref('base.rateUSDbis').unlink()
        except ValueError:  # pylint: disable=except-pass
            pass
        curr.rate_ids.rate = rate

    # Though, because on default EUR currency has rate of 1, we base
    # our computation from this currency.
    eur = self.browse_ref('base.EUR')
    company_currency = self.env.user.company_id.currency_id
    if company_currency == eur:
        usd = self.browse_ref('base.USD')
        if mode == 'over_limit':
            set_rate(usd, 0.01)
        else:
            set_rate(usd, 100)
        record[currency_fld] = usd.id
    else:
        if mode == 'over_limit':
            set_rate(company_currency, 100)
        else:
            set_rate(company_currency, 0.01)
        record[currency_fld] = eur.id


class AccessCase(common.TransactionCase):
    """Class that adds access rights/rules asserts."""

    _MODES_MAP = {
        'r': 'read',
        'w': 'write',
        'c': 'create',
        'u': 'unlink',
    }

    @classmethod
    def _prepare_pass_fail_modes(cls, modes=''):
        modes_map = cls._MODES_MAP
        pass_modes = {modes_map[m] for m in modes}
        all_modes = frozenset(modes_map.values())
        return pass_modes, all_modes - pass_modes

    def assertAccessRights(self, models, modes='rwcu', user=None):
        """Test access rights on specified model.

        Args:
            models (any): empty redordset or list of empty recordsets
                to test access rights for.
            modes (str): Read/Write/Create/Unlink modes to test on.
                Modes are written as 'rwcu' where each letter stands for
                its mode. If not set, it means access must fail for all
                modes. If set, then access must pass for specified ones
                and fail for remaining (default: {'rwcu'}).
            user (res.users): user to test access with. If not set, will
                use base.user_demo (default: {None}).

        Returns:
            None

        Raises:
            AccessError

        """
        self._assert_access(models, modes=modes, user=user)

    def assertAccessRightsSpec(self, spec, user=None):
        """Test access rights spec on multiple models for user.

        Spec key acts as identifier where user is expected to have
        access and missing modes in a key act as missing access and is
        expected that user wont have that access. If key is empty, it
        means no access is expected for specified models.

        Args:
            spec (dict): Expected structure:
                {
                    'rw': ['model1', 'model2'],
                    'r': ['model3', 'model4'],
                    '': ['model5'],
                    ...
                    ...
                }
            user (res.users): user to test access with. If not set, will
                use base.user_demo (default: {None}).

        Returns:
            None

        Raises:
            AccessError

        """
        for modes, model_names in spec.items():
            for model in [self.env[mname] for mname in model_names]:
                self.assertAccessRights(model, modes=modes, user=user)

    def assertAccessRule(self, records, modes='rwcu', user=None):
        """Test access rules on specified records.

        Args:
            records (any): any recordset to test on.
            modes (str): Read/Write/Create/Modes to test on. Modes are
                written as 'rwcu' where each letter stands for its mode.
                If not set, it means access must fail for all modes. If
                set, then access must pass for specified ones and fail
                for remaining (default: {'rwcu'}).
            user (res.users): user to test access with. If not set, will
                use base.user_demo (default: {None}).

        Returns:
            None

        Raises:
            AccessError

        """
        self._assert_access(records, modes=modes, user=user)

    def _assert_access(self, objects, modes=None, user=None):
        pass_modes, fail_modes = self._prepare_pass_fail_modes(modes=modes)
        objects_w_user = self._set_objects_with_user(objects, user=user)
        if pass_modes:
            self._assert_access_pass(objects_w_user, pass_modes)
        if fail_modes:
            self._assert_access_fail(objects_w_user, fail_modes)

    def _get_access_method_data(self, objects, modes):
        for obj in objects:
            for mode in modes:
                yield (obj.check_access, obj, mode)

    def _get_access_check_items(self, objects, modes):
        if not objects:
            objects = [objects]
        for obj in objects:
            for mode in modes:
                yield (obj, mode)

    def _assert_access_pass(self, objects, modes):
        for obj, mode in self._get_access_check_items(objects, modes):
            try:
                obj.check_access(mode)
            except AccessError as e:
                self.fail(f"{obj} obj was expected to pass. ({e})")

    @mute_logger(BASE_MODELS_PATH, BASE_RULE_PATH)
    def _assert_access_fail(self, objects, modes):
        for obj, mode in self._get_access_check_items(objects, modes):
            with self.assertRaises(AccessError):
                obj.check_access(mode)
                self.fail(f"AccessError not raised for obj: {obj}, mode: {mode}")

    def _get_default_access_user(self):
        return self.env.ref('base.user_demo')

    def _set_objects_with_user(self, objects, user=None):
        if not user:
            user = self._get_default_access_user()
        # We got list of different recordsets here.
        if isinstance(objects, (list, tuple)):
            return [obj.with_user(user) for obj in objects]
        return objects.with_user(user)


class TestBaseCommon(AccessCase):
    """Common class for all purpose tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for all purpose tests."""
        super().setUpClass()
        # Models.
        cls.IrModel = cls.env['ir.model']
        cls.IrConfigParameter = cls.env['ir.config_parameter']
        cls.ResCompany = cls.env['res.company']
        cls.ResPartner = cls.env['res.partner']
        cls.ResUsers = cls.env['res.users']
        # Companies.
        cls.company_main = cls.env.ref('base.main_company')
        # Users.
        cls.user_portal = cls.env.ref('base.demo_user0')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_root = cls.env.ref('base.user_root')
        # Models with Demo user
        cls.ResPartnerDemo = cls.ResPartner.with_user(cls.user_demo)
        # Partners.
        cls.partner_main = cls.env.ref('base.main_partner')
        cls.partner_portal = cls.user_portal.partner_id
        cls.partner_demo = cls.user_demo.partner_id
        cls.partner_admin = cls.user_admin.partner_id
        cls.partner_root = cls.user_root.partner_id
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.partner_azure_brandon = cls.env.ref('base.res_partner_address_15')
        # Groups
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_system = cls.env.ref('base.group_system')
        # Countries
        cls.country_lt = cls.env.ref('base.lt')
        cls.country_us = cls.env.ref('base.us')

    @classmethod
    def disable_mail_options(cls):
        """Disable some of the mailing options, to speed up tests."""
        cls.env = cls.env['base'].with_context(**DISABLED_MAIL_CONTEXT).env

    @classmethod
    def enable_mail_options(cls):
        """Enable some of the mailing options.

        This is counter call for disable_mail_options.
        """
        cls.env = cls.env['base'].with_context(**ENABLED_MAIL_CONTEXT).env

    def assertRecordSameValues(self, records, expected_values):
        """Wrap assertRecordValues to compare same vals on all recs."""
        expected_values_lst = [expected_values for i in range(len(records))]
        self.assertRecordValues(records, expected_values_lst)

    @classmethod
    def _get_model_id(cls, model_name):
        return cls.IrModel._get(model_name).id

    @classmethod
    @deprecated
    def _update_create_date(cls, records, dt):
        return update_create_date(records, dt)

    def _load(self, path_to_load, module_to):
        """Load resources for testing purposes.

        Args:
            path_to_load (str): absolute file path, or relative path
                within any `addons_path` directory.
            module_to (str): the name of the module to which the
                resource is to be loaded.

        """
        convert_file(
            self.cr,
            module_to,
            file_path(path_to_load),
            {},
            'init',
            False,
            'test',
        )


class TestBusCommon(TestBaseCommon):
    """Common test class for using bus functionality.

    `bus` module must be installed for this class to be usable.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common data for bus module functionality tests."""
        super().setUpClass()
        cls.BusPresence = cls.env['bus.presence']

    @classmethod
    def _create_update_bus_presence(
        cls, user, dt_poll=None, dt_presence=None, invalidate=True
    ):
        now = Datetime.now()
        if dt_poll is None:
            dt_poll = now
        if dt_presence is None:
            dt_presence = now
        vals = {}
        if dt_poll:
            vals['last_poll'] = dt_poll
        if dt_presence:
            vals['last_presence'] = dt_presence
        bus_presence = cls.BusPresence.search([('user_id', '=', user.id)])
        if bus_presence:
            bus_presence.write(vals)
        else:
            vals['user_id'] = user.id
            bus_presence = cls.BusPresence.create(vals)
        if invalidate:
            user.flush()
            user.invalidate_cache()
        return bus_presence

    @classmethod
    def _make_user_online(cls, user, invalidate=True):
        # By default gonna pass current time, so IM status will become
        # online.
        return cls._create_update_bus_presence(user, invalidate=invalidate)

    @classmethod
    def _make_user_away(cls, user, invalidate=True):
        # Make last activity 1 day old to make sure its treated as
        # away.
        yesterday = Datetime.now() - timedelta(days=1)
        return cls._create_update_bus_presence(
            user, dt_presence=yesterday, invalidate=invalidate
        )

    @classmethod
    def _make_user_offline(cls, user, invalidate=True):
        # Make last presence 1 day old to make sure its treated as
        # offline.
        yesterday = Datetime.now() - timedelta(days=1)
        return cls._create_update_bus_presence(
            user, dt_poll=yesterday, invalidate=invalidate
        )


class TestMailCommon(TestBaseCommon):
    """Common class for mail related tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for mail tests."""
        super().setUpClass()
        cls.MailMail = cls.env['mail.mail']
        cls.MailNotification = cls.env['mail.notification']
        cls.MailAlias = cls.env['mail.alias']
        cls.MailMessage = cls.env['mail.message']
        cls.MailThread = cls.env['mail.thread']
        cls.MailComposeMessage = cls.env['mail.compose.message']
        cls.MailSubtype = cls.env['mail.message.subtype']

    def _prepare_message_object(
        self, email_from, email_to, subject=None, body=None, options=None
    ):
        if not options:
            options = {}
        message = EmailMessage()
        message_id = options.get('message_id')
        if message_id:
            message['Message-Id'] = message_id
        # Explicit False means, to not set Message-Id
        elif message_id is not False:
            # Mimic default message_id from original.
            message_id = "<%s@localhost>" % time.time()
        references = options.get('references')
        if references:
            message['References'] = references
        message['From'] = email_from
        message['To'] = email_to
        if options.get('cc'):
            message['Cc'] = options['cc']
        if subject is not None:
            message['Subject'] = subject
        if body is not None:
            message.set_content(body)
        return message

    def _inject_message_id(self, record, message_id):
        """Inject message with message_id on target record.

        Used to make thread "replyable".
        """
        message = record.message_post(body='DUMMY BODY')
        message.message_id = message_id
        return message

    def _prepare_message_object_as_reply(
        self,
        email_from,
        email_to,
        record,
        subject,
        body,
        tracking_message_id,
        options=None,
    ):
        """Force create fake message and reference it on new msg.

        This act makes second message act as its replying to thread.
        """
        # Need to use Odoo specific pattern, so it would then be matched
        # with regex.
        tracking_message_id = generate_tracking_message_id(tracking_message_id)
        self._inject_message_id(record, tracking_message_id)
        if not options:
            options = {}
        options['references'] = tracking_message_id
        return self._prepare_message_object(
            email_from, email_to, subject, body, options=options
        )


class TestMailActivityCommon(TestBaseCommon):
    """Utility class for more convenient mail activity tests.

    `mail` module must be installed for this class to be usable.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common data for mail activity tests."""
        super().setUpClass()
        cls.MailActivity = cls.env['mail.activity']
        cls.activity_type_email = cls.env.ref('mail.mail_activity_data_email')
        cls.activity_type_call = cls.env.ref('mail.mail_activity_data_call')
        cls.activity_type_meeting = cls.env.ref('mail.mail_activity_data_meeting')
        cls.activity_type_todo = cls.env.ref('mail.mail_activity_data_todo')

    @classmethod
    def _get_default_methods_for_activity_fields(self):
        return {
            'res_id': lambda r: r.id,
            'res_model_id': lambda r: self._get_model_id(r._name),
            'summary': lambda r: 'Dummy Summary',
            'activity_type_id': lambda r: self.activity_type_todo.id,
        }

    @classmethod
    def _prepare_activity(self, record, vals=None):
        if not vals:
            vals = {}
        res = self._get_default_methods_for_activity_fields()
        for key, default_method in res.items():
            if key not in vals:
                vals[key] = default_method(record)
        return vals

    @classmethod
    def _create_activity(self, record, vals=None, user=None):
        vals = self._prepare_activity(record, vals=vals)
        activity = self.MailActivity.create(vals)
        if user:
            return activity.with_user(user)
        return activity


class TestHelpdeskCommon(TestBaseCommon):
    """Common test class for using helpdesk functionality.

    `helpdesk` module must be installed for this class to be usable.
    """

    @classmethod
    def setUpClass(cls):
        """Set up data for helpdesk module functionality tests."""
        super().setUpClass()
        cls.HelpdeskTeam = cls.env['helpdesk.team']
        cls.HelpdeskTicket = cls.env['helpdesk.ticket']
        cls.HelpdeskSla = cls.env['helpdesk.sla']
        cls.helpdesk_team_1 = cls.env.ref('helpdesk.helpdesk_team1')
        cls.helpdesk_ticket_1 = cls.env.ref('helpdesk.helpdesk_ticket_1')
        cls.helpdesk_ticket_2 = cls.env.ref('helpdesk.helpdesk_ticket_2')
        cls.helpdesk_sla_1 = cls.env.ref('helpdesk.helpdesk_sla_1')
        cls.helpdesk_sla_2 = cls.env.ref('helpdesk.helpdesk_sla_2')
        cls.helpdesk_stage_new = cls.env.ref('helpdesk.stage_new')
        cls.helpdesk_stage_in_progress = cls.env.ref('helpdesk.stage_in_progress')
        cls.helpdesk_stage_solved = cls.env.ref('helpdesk.stage_solved')
        cls.helpdesk_stage_cancelled = cls.env.ref('helpdesk.stage_cancelled')
        cls.ticket_type_question = cls.env.ref('helpdesk.type_question')
        cls.ticket_type_issue = cls.env.ref('helpdesk.type_incident')


class TestOdootilCommon(TestBaseCommon):
    """Common class for all odootil test cases."""

    @classmethod
    def setUpClass(cls):
        """Set up common data."""
        super().setUpClass()
        cls.Odootil = cls.env['odootil']
        cls.partner_1 = cls.env.ref('base.res_partner_1')
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        cls.partner_3 = cls.env.ref('base.res_partner_3')
        cls.partner_4 = cls.env.ref('base.res_partner_4')


class TestAccountCommon(TestBaseCommon):
    """Common test class for using account functionality.

    `account` module must be installed for this class to be usable.
    """

    @classmethod
    def setUpClass(cls):
        """Set up common data for tests."""
        super().setUpClass()
        cls.AccountMove = cls.env['account.move']
        cls.AccountMoveLine = cls.env['account.move.line']
        cls.AccountAccount = cls.env['account.account']
        cls.AccountJournal = cls.env['account.journal']
        cls.AccountTax = cls.env['account.tax']
        cls.AccountPaymentRegister = cls.env['account.payment.register']

    def register_payment(self, move, payment_vals=None):
        """Register payment.

        Arguments:
            move (recordset): move to register payment.
            payment_vals (dict): payment values, e.g. amount, payment_date.

        """
        # Note. If no payment_vals, invoice will be paid in full.
        if not payment_vals:
            payment_vals = {}
        ctx = {'active_model': 'account.move', 'active_ids': move.ids}
        register_payments = self.AccountPaymentRegister.with_context(**ctx).create(
            payment_vals
        )
        register_payments._create_payments()
