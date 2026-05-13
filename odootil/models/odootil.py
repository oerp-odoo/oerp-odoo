import operator
from collections import defaultdict

import email_validator
import validators
from footil.formatting import email_to_alias_and_domain, strip_space
from lxml import etree
from num2words import num2words

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round
from odoo.tools.misc import frozendict

from odoo.addons.base.models.ir_sequence import IrSequence

from ..tools.email import is_email_in_domains

NON_WRITABLE_KEYS = ['id']
PSQL_DESC = 'desc'
# Common constants.
PRIORITY = [('1', 'Low'), ('2', 'Normal'), ('3', 'High')]
DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
VAT_KEY = 'vat'
# TODO: might be implemented to be configured via res.country
VAT_FORMATTING_IGNORE_COUNTRY_CODES = ('CH',)

# Cache for singleton records.
singleton_records = {}


class Interpolation:
    """Interpolate string using datetime variables.

    Attaching already existing implementation from ir.sequence model.
    """

    def __init__(self, prefix='', suffix='', _name='', _context=None):
        """Initialize Interpolation class for string rendering."""
        self.prefix = prefix
        self.suffix = suffix
        self._name = _name
        self._context = _context or {}

    def ensure_one(self):
        """Implement fake ensure_one."""
        # Ensure one is called inside `_get_prefix_suffix`.
        return True

    # Need to implement this method, because _get_prefix_suffix expects
    # it, so we mimic that.
    def get(self, name):
        """Implement odoo model's 'get' method interface."""
        # name argument is ignored here actually, we only pass it,
        # because of attached method requirement.
        return self._name

    get_prefix_suffix = IrSequence._get_prefix_suffix


class Odootil(models.AbstractModel):
    """Model to add some common functionality patterns for modules.

    Provided methods can be used as helpers for better re-usability.
    """

    _name = 'odootil'
    _description = 'Odoo Utilities'

    # String manipulation helpers.

    @api.model
    def get_monetary_format(
        self,
        currency,
        value,
        lang_code=False,
        use_symbol=False,
        decimal_places=None,
        rounding=None,
    ):
        """Return monetary form of float value.

        Args:
            currency (recordset): res.currency record
            value (float): float value to be formatted
            lang_code (str): code of language (locale code),
                e.g. 'en_US'
            use_symbol (bool): whether to include currency symbol or not
                (default: {False}).
            decimal_places (int): custom position of a digit to the
                right of a decimal point. Otherwise, will use value
                from currency.
            rounding (float): value to be rounded off to the nearest
                multiple of the given rounding. Otherwise, will use
                rounding from currency.

        Returns:
            str: monetary form of float value.

        """
        lang_code = (
            lang_code or self.env.user.lang or self._context.get('lang', 'en_US')
        )
        lang = self.env['res.lang']._lang_get(lang_code)
        fmt = '%.{}f'.format(
            decimal_places if decimal_places is not None else currency.decimal_places
        )
        # Currency and language specific output.
        # `format` with `grouping` and `monetary` enabled returns
        # monetary format for float values.
        rounded_value = float_round(
            value, precision_rounding=rounding or currency.rounding
        )
        value = lang.format(fmt, rounded_value, grouping=True, monetary=True)
        if use_symbol:
            if currency.position == 'before':
                args = (currency.symbol, value)
            else:
                args = (value, currency.symbol)
            return '%s %s' % args
        else:
            return value

    @api.model
    def get_num2words(self, number, options=None):
        """Check if valid to use num2words, get number in words."""
        if not options:
            options = {}
        ordinal = options.get('ordinal', False)
        lang = (
            options.get('lang')
            or self.env.user.lang
            or self._context.get('lang', 'en_US')
        )
        to = options.get('to', 'cardinal')
        kwargs = options.get('kwargs', {})
        try:
            return num2words(number, ordinal=ordinal, lang=lang, to=to, **kwargs)
        except NotImplementedError:
            fallback_words = options.get('fallback_words')
            if fallback_words is not None:
                return fallback_words
            raise

    # Sequence number wrapper.

    @api.model
    def get_sequence_number(self, code=None, sequence=None, company_id=None):
        """Get sequence number by code or by sequence record.

        company_id is ignored if sequence number is retrieved by
        sequence record.

        Args:
            code (str): sequence record code (default: {None})
            sequence (recordset): sequence record (default: {None})
            company_id (int): company ID to use in search with sequence
                code (default: {None})

        Returns:
            str: next sequence number by sequence record.

        """
        if code:
            IrSequence = self.env['ir.sequence']
            if company_id:
                return IrSequence.with_company(company_id).next_by_code(code)
            return IrSequence.next_by_code(code)
        if sequence:
            return sequence.next_by_id()

    @api.model
    def set_sequence_number(
        self,
        vals,
        key,
        code=False,
        sequence=False,
        company_id=False,
        default=None,
    ):
        """Set sequence number on specified dictionary key.

        sequence number getter uses method get_sequence_number.

        Args:
            vals (dict): dictionary to have sequence set on.
            key (str): vals key to set sequence number on.
            code (str): sequence record code to use in search
                (default: {False})
            sequence (recordset): sequence record to use
                (default: {False})
            company_id (int): company ID to use in seq search
                (default: {False})
            default (str): default sequence number value if sequence
                can't be found (default: {False}).

        Returns:
            None

        """
        if not vals.get(key):
            if default is None:
                default = _('New')
            seq_number = self.get_sequence_number(
                code=code, sequence=sequence, company_id=company_id
            )
            vals[key] = seq_number or default

    # Environment and database operation helpers.

    @api.model
    def update_external_ids_module(self, names, module, module_new):
        """Update module name of external identifiers.

        This might be reused as hook or in .yml file, when some elements
        (which have external identifiers) were moved from one module to
        another and external identifiers have left unchanged.

        Args:
            names (list): list of full names of external identifiers,
                excluding module name, e.g. 'field_res_partner_name'.
            module (str): module name set on external identifier,
                e.g. 'sale_order'.
            module_new (str): name of module to set on external identifier,
                e.g. 'sale_order_extended'.

        """
        # We expect to get a single record for each name, because there
        # is an unique constraint (module, name).
        identifiers = self.env['ir.model.data'].search(
            [('name', 'in', names), ('module', '=', module)]
        )
        if identifiers:
            identifiers.write({'module': module_new})

    # recordset helpers.

    # TODO: investigate if this method is still relevant.
    def group_records_by_company(self, records):
        """Group records by Company ID.

        Heuristics to use appropriate company:
            - Model has company_id field, using company_id ID if its
                truthy.
            - Otherwise use current user company ID.
        """
        user_company_id = self.env.user.company_id.id
        Model = self.env[records._name]
        if not hasattr(Model, 'company_id'):
            return {user_company_id: records}
        result = defaultdict(lambda: Model)
        for record in records:
            company_id = record.company_id.id or user_company_id
            result[company_id] |= record
        return result

    # Context helpers

    def update_request_context(self, request, **kwargs):
        """Update context on request object."""
        old_ctx = request.context.copy()
        request.context = frozendict(dict(old_ctx, **kwargs))

    # ir.actions helpers.

    def prepare_message_compose_act(
        self,
        template_xml_id,
        composer_form_xml_id=None,
        target='new',
        attachments_data=None,
    ):
        """Prepare message composer.

        Args:
            template_xml_id (str): full xml id of `mail.template` to be used.
            composer_form_xml_id (str): full xml id of `mail.compose.message`
                form view.
            target (str): defines where new composer window should be
                opened (default - open in new window). Available values:
                'current', 'new', 'inline', 'fullscreen', 'main'.
            attachments_data (list): list of dictionaries with valid
                values for `ir.attachment` records to be created.

        """
        # `context` might contain extra defaults for
        # `mail.compose.message` or `mail.message`, such as `res_id`,
        # `model`, `composition_mode` and etc.
        template = self.env.ref(template_xml_id)
        context = dict(
            self._context,
            default_use_template=bool(template),
            default_template_id=template.id,
        )
        composer_form_view = composer_form_xml_id or self.env.ref(
            'mail.email_compose_message_wizard_form'
        )
        attachments = Attachment = self.env['ir.attachment']
        for values in attachments_data:
            attachments |= Attachment.create(values)
        if attachments:
            context['default_attachment_ids'] = [(6, 0, attachments.ids)]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(composer_form_view.id, 'form')],
            'view_id': composer_form_view.id,
            'target': target,
            'context': context,
        }

    # Date helpers.

    @api.model
    def check_dates_range(self, date_earlier, date_later, allow_equal=True, msg=None):
        """Validate two dates and raise if condition is not satisfied.

        Args:
            date_earlier (str, date, datetime): date which should be
                earlier.
            date_later (str, date, datetime): date which should be
                later.
            allow_equal (bool): defines if dates are allowed to be
                equal (default: {True}).
            msg (str): custom exception message (default: {None}).

        """
        _operator = operator.gt if allow_equal else operator.ge
        if _operator(date_earlier, date_later):
            msg = msg or _("Date From must be earlier than %sDate To.") % (
                _("or equal to ") if allow_equal else ""
            )
            raise UserError(msg)

    @api.model
    def get_months_selection(self):
        """Return list of months with their indexes."""
        # Could be a constant, but constants don't support translations.
        return [
            (1, _("January")),
            (2, _("February")),
            (3, _("March")),
            (4, _("April")),
            (5, _("May")),
            (6, _("June")),
            (7, _("July")),
            (8, _("August")),
            (9, _("September")),
            (10, _("October")),
            (11, _("November")),
            (12, _("December")),
        ]

    # Compute amount helpers.

    @api.model
    def get_cost(self, product, uom, options=None):
        """Return unconverted cost for product.

        It will return price's original currency alongside.
        Possible one of four cases:
          - if order is 'standard' and standard_price is not False, will
                return it.
          - if order is 'supplier', will return seller/vendor price if
                it's set.
          - if order is 'bom', will return cost calculated from bom if
                product has one.
          - if none of the above is set, will default to 0.

        Args:
            product (recordset): product.product object for which cost
                should be calculated.
            uom (recordset): uom.uom recordset.
            options (dict): custom options to get cost price. Supported
                keys:
                - quantity (float): quantity for which cost should be
                    get (default {0.0}).
                - date (datetime.date): date to get cost.
                - cost_methods (tuple): defines in what order cost will
                    be calculated (which type of cost method must be
                    checked first). Default: {('standard', 'supplier')}.

        Returns:
            cost, res.currency recordset, cost method
            float, recordset, str

        """
        if not options:
            options = {}
        company_currency = self.env.user.company_id.currency_id

        def get_standard_cost():
            if product.standard_price:
                return product.standard_price, company_currency

        def get_supplier_cost():
            if product.seller_ids:
                seller = product._select_seller(
                    quantity=options.get('quantity', 0.0),
                    date=options.get('date', None),
                    uom_id=uom,
                )
                # because might not match and return empty rec.
                if seller:
                    return seller.price, seller.currency_id

        def get_bom_cost():
            # :rtype: defaultdict(`lambda: self.env['mrp.bom']`)
            bom = self.env['mrp.bom']._bom_find(products=product)[product]
            if bom:
                uom_ratio = uom._compute_quantity(1.0, bom.product_uom_id, round=False)
                # Quantity which is requested is important, because
                # depending on quantity, BOM cost price might
                # variate.
                factor = (options.get('quantity') or 1) * uom_ratio
                # BOM Structure & Cost report already calculates all
                # needed values and we can reuse them.
                bom_data = self.env['report.mrp.report_bom_structure']._get_bom(
                    bom_id=bom.id, product_id=product, line_qty=factor
                )
                # We except UOM ratio when it is below 1.0,
                # because total is already counted for 1 UOM and
                # there is no need to do extra conversions.
                price = bom_data['total']
                if uom_ratio >= 1.0:
                    price = price / bom_data['bom_qty'] * uom_ratio
                # Its a dilemma here, because get_cost is
                # supposed to return unconverted price, though
                # to get correct price, need to specify
                # converted quantity for BOM. To workaround
                # that, converting back to product UOM.
                price = uom._compute_price(price, product.uom_id)
                return price, self.env.user.company_id.currency_id

        for cost_method in options.get('cost_methods', ('standard', 'supplier')):
            cost_tuple = locals()['get_%s_cost' % cost_method]()
            if cost_tuple:
                return cost_tuple + (cost_method,)

        return 0.0, company_currency, False

    @api.model
    def convert_order_float_to_other_curr(self, order, amount, to_currency):
        """Convert some order amount to another currency if needed."""
        date = order.date_order or fields.Date.today()
        from_currency = order.pricelist_id.currency_id
        if from_currency != to_currency:
            amount = from_currency._convert(amount, to_currency, order.company_id, date)
        return amount

    # Other constraint helpers

    @api.model
    def check_url(self, url):
        """Check URL validity.

        Args:
            url (str): url to check

        Returns:
            None

        Raises:
            ValidationError if not valid

        """
        if self.env.context.get('skip_check_url'):
            return
        # Using '' as default, to make sure False value is not passed,
        # which cant be validated by validators.url.
        if not validators.url(url or ''):
            raise ValidationError(_("'%s' is not valid URL.") % url)

    # Mail helpers

    @api.model
    def filter_mail_aliases(self, emails_lst):
        """Remove emails that are email aliases in Odoo.

        Will use catchall domain to compare with email domain part and
        then check if alias part exists as Odoo mail alias.

        Args:
            emails_lst (list): List of email addresses to filter. Must
                be raw emails only (no email name etc).

        Returns:
            emails that are not Odoo mail aliases.
            list

        """
        domain_catchall = (
            self.env['ir.config_parameter'].sudo().get_param('mail.catchall.domain')
        )
        if not domain_catchall:
            return emails_lst
        emails_to_keep = []
        MailAlias = self.env['mail.alias']
        for email in emails_lst:
            alias, domain = email_to_alias_and_domain(email)
            if (
                alias
                and domain == domain_catchall
                and MailAlias.search_count([('alias_name', '=', alias)])
            ):
                continue
            emails_to_keep.append(email)
        return emails_to_keep

    @api.model
    def validate_email(self, email, whitelisted_domains=None, **kw):
        """Validate given email.

        NOTE: this validation does not ensure that given email is an
        actual email. It only checks if given email is close to correct
        email format w/o any extra data.

        Args:
            email (str): email to validate.
            whitelisted_domains (tuple): tuple of domains to ignore
                deliverability.

        Returns:
            True if email is valid, raise ValidationError otherwise.

        """
        if self.env.context.get('odootil_no_email_validation'):
            return True
        # Disable deliverability check on whitelisted domains.
        if 'check_deliverability' not in kw and whitelisted_domains is not None:
            kw['check_deliverability'] = not is_email_in_domains(
                email, whitelisted_domains
            )
        try:
            email_validator.validate_email(email, **kw)
        except email_validator.EmailNotValidError as e:
            raise ValidationError(
                _("Email '%(email)s' is incorrect. %(err)s", email=email, err=e)
            )
        return True

    # Find country by vat helpers

    @api.model
    def find_country_by_vat(self, vat):
        """Extract country code from vat.

        Args:
            vat (str): vat of country e.g. 'LT100010958410'

        Returns:
            res.country

        """
        if len(vat) >= 2:
            return self.find_country_by_code(vat[:2].upper())
        return self.env['res.country']

    @api.model
    def find_country_by_code(self, code):
        """Find country by extracted country code."""
        return self.env['res.country'].search([('code', '=', code)])

    # View helpers

    @api.model
    def insert_arch_xml(self, arch_etree, xpath, view_xmlid, position):
        """Include custom view arch to another arch etree.

        Args:
            arch_etree (lxml.etree): etree element to which custom view
                arch will be inserted to.
            xpath (str): xpath of arch_etree to identify custom view
                insertion place.
            view_xmlid (str): XML ID of custom view to insert.
            position (int): describes where view should be inserted
                according to element place, e.g. 0 - before, 3 - after
                3rd element.

        """
        xpath_etree = arch_etree.findall(xpath)
        if xpath_etree:
            view_extension = self.env.ref(view_xmlid)
            view_extension_etree = etree.fromstring(view_extension.arch)  # nosec: B320
            xpath_etree[0].insert(position, view_extension_etree)
        return arch_etree

    # TODO: This could be even removed because some of countries allows to
    # have VAT with spaces. Also, standard odoo has some logic for fixing
    # VAT codes itself.
    def update_vat_no_space(self, vals):
        if vals.get(VAT_KEY):
            country = self.find_country_by_vat(vals[VAT_KEY])
            # Format VAT without any spaces for specific countries
            if country.code not in VAT_FORMATTING_IGNORE_COUNTRY_CODES:
                vals[VAT_KEY] = strip_space(vals[VAT_KEY])
