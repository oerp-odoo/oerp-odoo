from __future__ import annotations

import itertools
from functools import partial
from types import SimpleNamespace

from footil.sorting import ReverseComparator

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.orm.identifiers import NewId
from odoo.orm.types import DomainType

PSQL_DESC = 'desc'


# TODO: check if this needed anymore. Odoo now should support better ordering
# from NewId itself.
class NewIdSorted(NewId):
    """Subclass for NewId to make it sortable with real record.

    Comparing is done in three ways:
        - Both have origin. Comparing origin.
        - Only one has origin. Less than is the one with origin.
        - None have origin. Comparing with pos (position).
    """

    id_iter = itertools.count()
    __slots__ = ('pos', '_pseudo_id')

    def __init__(self, origin=None, ref=None, pos=0):
        """Override to include original position in recordset."""
        super().__init__(origin=origin, ref=ref)
        self.pos = pos
        self._pseudo_id = next(self.id_iter)

    def __lt__(self, other):
        """Compare int or other NewIdSorted object."""
        if self.origin and other.origin:
            return self.origin < other.origin
        # The one with origin is less than without origin.
        if not self.origin and other.origin:
            return False
        if self.origin and not other.origin:
            return True
        # None have origin. Comparing with position.
        return self.pos < other.pos

    def __repr__(self):
        """Return reproducible object in string."""
        class_name = self.__class__.__name__
        return '%s(origin=%s, pos=%s)' % (class_name, self.origin, self.pos)


class Base(models.AbstractModel):
    """Extend to add odootil helper methods."""

    _inherit = 'base'

    # Check helpers.

    def _validate_fields(self, field_names, excluded_names=()):
        """Extend to handle deferred.validation.mixin context."""
        exclusion_map = self.env.context.get('deferred_validation_exclusion_map')
        if exclusion_map:
            excluded_names = set(excluded_names)
            for recs, extra_excluded_names in exclusion_map.items():
                if recs._name != self._name:
                    continue
                excluded_names |= extra_excluded_names
            # Convert back to tuple to keep expected type.
            excluded_names = tuple(excluded_names)
        return super()._validate_fields(field_names, excluded_names=excluded_names)

    def __prepare_search_multicompany_method(
        self, domain, offset=0, limit=None, order=None, options=None
    ):
        def is_multi_comp_used(multi_comp_rule_xml_id, company_id):
            # Multi company is used, if there is explicit rule to
            # enable/disable it or if company_id was passed as argument.
            # Multi company rule takes priority.
            if multi_comp_rule_xml_id:
                # Rule that defines if multi-company rule is enabled (
                # shared globally or per company)
                return (
                    self.sudo().env.ref(multi_comp_rule_xml_id).active
                    # Can filter per company, only if company is passed,
                    # otherwise would filter for partners that have no
                    # company set only.
                    and company_id
                )
            return bool(company_id)

        def get_company_domain(multi_comp_rule_xml_id, company_id):
            if is_multi_comp_used(multi_comp_rule_xml_id, company_id):
                return [('company_id', 'in', [company_id, False])]
            return []

        def to_multicompany_domain(domain):
            company_domain = get_company_domain(
                options.get('multi_comp_rule_xml_id'),
                options.get('company_id', False),
            )
            return Domain.AND([domain, company_domain])

        def _search_multicompany_method(count=False):
            return self.with_context(active_test=active_test).search(
                domain, offset=offset, limit=limit, order=order
            )

        if not options:
            options = {}
        domain = to_multicompany_domain(domain)
        active_test = options.get('active_test', False)
        return _search_multicompany_method

    # Search helpers.

    @api.model
    def search_multicompany(
        self, domain, offset=0, limit=None, order=None, options=None
    ):
        """Find multi-company friendly records by domain.

        Intended to be used for fields where value uniqueness must be
        preserved.

        Uniqueness checked globally if objects are shared across
        multiple companies, otherwise current object company is used.

        Args:
            domain: base domain for search. Should not include
                multi-company leaf.
            offset (int): number of results to ignore (default: {0})
            limit (int): maximum number of records to return (default:
                {None})
            order (str): sort string (default {None})
            options (dict): extra options to modify search. Dict can
                    have such keys. (default: {None}):
                multi_comp_rule_xml_id (str): multi company ir.rule
                    XMLID that is used to identify if multi-company is
                    used for that object. Optional (default: {None}).
                company_id (int): company ID that is used for multi
                    company domain. If multi_company_rule_xml_id is not
                    used and company_id is specified, it will be force
                    used in domain. Optional (default: {False}).
                active_test (bool): whether to include inactive records.
                    False value means include (default: {False}).

        Returns:
            recordset

        """
        return self.__prepare_search_multicompany_method(
            domain, offset=offset, limit=limit, order=order, options=options
        )()

    @api.model
    def search_with_total_count(
        self, domain, limit=None, offset=0, order=None
    ) -> tuple[Base, int]:
        records = self.search(domain, limit=limit, offset=offset, order=order)
        if limit and len(records) == limit:
            total_count = self.search_count(domain)
        else:
            total_count = len(records) + offset
        return (records, total_count)

    @api.model
    def _is_company_id_for_search_applicable(self, company_id, args):
        return (
            # False is valid value
            company_id is not None
            and 'company_id' in self._fields
            and not any(
                arg and not isinstance(arg, str) and arg[0] == 'company_id'
                for arg in args
            )
        )

    @api.model
    def _search(
        self,
        domain: DomainType,
        offset: int = 0,
        limit: int | None = None,
        order: str | None = None,
        *,
        active_test: bool = True,
        bypass_access: bool = False,
    ):
        company_id = self.env.context.get('company_id_for_search')
        if self._is_company_id_for_search_applicable(company_id, domain):
            domain = Domain.AND(
                [
                    # Must include False to cover global records.
                    domain,
                    [('company_id', 'in', (company_id, False))],
                ]
            )
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )

    # orderby transformation helpers.

    @api.model
    def to_writable_keys(self, keys):
        """Filter keys, leaving only those that could be writable."""
        return [k for k in keys if k not in models.MAGIC_COLUMNS]

    @api.model
    def _orderby_to_items(self, order_spec=None):
        order_spec = order_spec or self._order
        for item in order_spec.split(','):
            # Remove leading white space that might be hanging after
            # splitting.
            item = item.lstrip()
            # E.g. 'name asc NULLS FIRST' -> ('name', 'asc NULLS FIRST')
            key, *options = item.split(' ', 1)
            options = options[0] if options else ''
            yield (key.replace(' ', ''), options)

    @api.model
    def orderby_to_keys(self, order_spec=None):
        """Transform Model's _order to list keys only.

        Strips all options, like asc, desc, NULLS {FIRST | LAST}.
        """
        return [item[0] for item in self._orderby_to_items(order_spec=order_spec)]

    @api.model
    def orderby_to_writable_keys(self, order_spec=None):
        """Transform Model's _order to list with writable keys."""
        return self.to_writable_keys(self.orderby_to_keys(order_spec=order_spec))

    @api.model
    def orderby_to_sort_keys(self, order_spec=None):
        """Transform Model's _order to list of tuple keys.

        First item in tuple is key, second boolean value, indicating if
        key order must be reversed (usually descending).
        """

        def is_reversed(options):
            return PSQL_DESC in options.lower()

        return [
            (i[0], is_reversed(i[1]))
            for i in self._orderby_to_items(order_spec=order_spec)
        ]

    @api.model
    def get_sort_key_function(self, sort_keys):
        """Return function that uses sort_keys for sort function.

        Takes into account reverse option, so comparison is done in
        reverse using ReverseComparator class.
        """
        return lambda x: tuple(
            ReverseComparator(x[k]) if rev else x[k] for (k, rev) in sort_keys
        )

    # recordset helpers.

    def get_record_index(
        self, record, start=0, end=None, msg=None, raise_if_not_found=True
    ):
        """Get lowest zero-based index as record value in recordset.

        Can specify optional range.

        Args:
            record (recordset): single record to find its index position
                in recordset.
            start (int): start index for recordset (default: {0})
            end (int): end index for recordset (default: {None})
            msg (str): custom exception message to use if record is not
                found inside recordset (default: {None}).
            raise_if_not_found (bool): raise ValidationError if record
                is not in recordset (default: {True})

        Returns:
            record index position in recordset or raise if not found, or
            -1 if not raising.
            int

        """
        if not end:
            end = len(self)
        if start > end:
            raise ValidationError(_("end index must be greater than start."))
        for i in range(start, end):
            if self[i] == record:
                return i
        if raise_if_not_found:
            if not msg:
                msg = _("%s is not in recordset") % record
            raise ValidationError(msg)
        return -1

    def sorted_virtual(self, order_spec=None, reverse=False):
        """Return sorted recordset. Records can have pseudo NewId.

        If order_spec has no 'id' column, it uses recordset `sorted`
        method.

        If need to sort by 'id', sort data from recordset is extracted
        into separate list and attributes are sorted like recordset,
        except for 'id' attribute. 'id' attribute is sorted using
        NewIdSorted class. Read NewIdSorted docstring about 'id'
        attribute sorting.

        Args:
            order_spec (str): sorting spec as used by attribute _order
                (default: {None}).
            reverse (bool): if sorted recordset is to be reversed
                (default: {False}).

        Returns:
            recordset: sorted recordset.

        """

        def create_data_to_sort(record, pos, keys):
            vals = {k: record[k] for k in keys}
            newid_kwargs = {'pos': pos}
            if record.id:  # real record
                newid_kwargs['origin'] = record.id
            else:  # virtual record
                newid_kwargs['ref'] = record.id.ref
            # False is NewId record that can have ref.
            vals['id'] = NewIdSorted(**newid_kwargs)
            return vals

        def to_sortable_with_map(keys):
            records_map = {}
            to_sort = []
            for pos, record in enumerate(self):
                data = create_data_to_sort(record, pos, keys)
                records_map[data['id']._pseudo_id] = record
                to_sort.append(data)
            return to_sort, records_map  # map is to convert back.

        def extract_sorted_records(sorted_data, records_map):
            sorted_recordset = self.env[self._name]
            for dummy in sorted_data:
                sorted_recordset |= records_map[dummy['id']._pseudo_id]
            return sorted_recordset

        order_keys = self.orderby_to_keys(order_spec)
        sort_keys = self.orderby_to_sort_keys(order_spec)
        key_func = self.get_sort_key_function(sort_keys)
        # Only need to hack, if order contains 'id'
        if 'id' in order_keys:
            to_sort, records_map = to_sortable_with_map(
                self.to_writable_keys(order_keys)
            )
            sorted_data = sorted(to_sort, key=key_func, reverse=reverse)
            return extract_sorted_records(sorted_data, records_map)
        return self.sorted(key=key_func, reverse=reverse)

    def new_multi(self, values=None, refs=None):
        """Return new virtual record using provided record values.

        This is wrapper for `new` method to handle multiple virtual
        records at once.

        Args:
            values (dict): extra values to use in update.
                (default: {None}).
            refs (iterable): list of references to NewId. Only used for
                empty recordset. Otherwise, record is passed as origin
                on new. (default: {None}).

        Returns:
            recordset with NewId.

        """

        def get_items_and_key():
            if self:
                return (self, 'origin')
            return (refs, 'ref')

        if not values:
            values = {}
        items, key = get_items_and_key()
        if items:
            new_recs = self.env[self._name]
            for item in items:
                new_recs |= self.new(values=values, **{key: item})
            return new_recs
        return self.new(values=values)

    def read_to_record(self, vals=None, dotnotation=False, fields=None, load=False):
        """Read records data and convert to record format.

        Args:
            vals (dict): cache format values dictionary to force update
                read values with extra ones (default: {None}).
            dotnotation (bool): whether to convert dictionary in
                SimpleNamespace object, to have dot notation (
                default: {False}).
            fields (list): list of fields to read. Falsy value means all
                fields (default: {None}).
            load (str): whether to use classic format (
                expects '_classic_read' value) (default: {False}).

        Returns:
            recordset read values converted to record format.
            list

        """

        def notation_converter():
            if dotnotation:
                return lambda vals: SimpleNamespace(**vals)
            return lambda vals: vals

        to_notation = notation_converter()
        datas = self.read(fields=fields, load=load)
        if vals:
            for data in datas:
                data.update(vals)
        return [to_notation(self._convert_to_record(data)) for data in datas]

    def prepare_write_vals(self, fnames: list[str]):
        """Convert record field names to write format vals.

        This is similar to standard _convert_to_write but here we specify
        field names to convert and simply read it from the record,
        opposed to just converting specified dictionary.

        This method is intended to be used, when you need to reuse
        cache, because `read` method would fetch directly from database.
        """
        self.ensure_one()
        vals = {}
        for fname in fnames:
            vals[fname] = self._fields[fname].convert_to_write(self[fname], self)
        return vals

    def sync_related_field_value(self, rel_record_fname, sync_fname, inverse=False):
        """Sync field from related record.

        NOTE: currently, sync-able field name on source and target
            models must match.

        Args:
            rel_record_fname (string): name of related field where
                from sync-able data will be taken from.
            sync_fname (string): name of field to sync.
            inverse: (bool): whether to inverse sync (default: {False}).

        """

        def resolve_sender_receiver(inverse, rec):
            if inverse:
                return rec, rec[rel_record_fname]
            return rec[rel_record_fname], rec

        f = partial(resolve_sender_receiver, inverse)
        for rec in self.filtered(rel_record_fname):
            sender, receiver = f(rec)
            if sender[sync_fname] != receiver[sync_fname]:
                receiver[sync_fname] = sender[sync_fname]

    # Selection field helpers.

    @api.model
    def get_selection_map(self, fname):
        """Return selection mapping for record field.

        Args:
            fname (str): selection field name

        Returns:
            selection in map form.
            dict

        """
        return dict(self._fields[fname]._description_selection(self.env))

    def get_selection_label(self, fname):
        """Return Label of current selection field value.

        If selection value is falsy, returns empty string. This might
        return unexpected results if one of the selection field values
        is falsy value. It is good practice to specify only truthy
        values for selection values.

        Args:
            fname (str): selection field name

        Returns:
            str: label of current selection field value.

        """
        self.ensure_one()
        val = self[fname]
        if not val:
            return ''
        selection_map = self.get_selection_map(fname)
        return selection_map[val]

    # Context helpers

    @api.model
    def get_active_data(self, single=False, msg=None, expected_model=None):
        """Validate context and return active data.

        Args:
            single (bool): check if active_ids can have only one element
                 in it (default: {False})
            msg (str): custom exception message if there is more than
                one active_id, when single=True used (default: {None})
            expected_model (str): Ensure that active model matches
                specified model.

        Returns:
            {'res_id': int, 'res_ids': list, 'model': str}

        """
        ctx = self.env.context
        try:
            model = ctx['active_model']
        except KeyError:
            raise ValidationError(
                _("Programming error: 'active_model' is missing in context")
            )
        if expected_model is not None and model != expected_model:
            raise ValidationError(
                _(
                    "Active Model '%(model)s' does not match expected model "
                    + "'%(expected_model)s'!",
                    model=model,
                    expected_model=expected_model,
                )
            )
        res_id = ctx.get('active_id', False)
        res_ids = ctx.get('active_ids', [])
        if not res_id:
            try:
                res_id = res_ids[0]
            except IndexError:
                raise ValidationError(
                    _(
                        "Programming error: at least 'active_id' or "
                        "'active_ids' key must be present in context"
                    )
                )
        elif not res_ids:
            res_ids = [res_id]
        if single and len(res_ids) > 1:
            exc_msg = msg or _("Only single active_id is allowed")
            raise ValidationError(exc_msg)
        return {'res_id': res_id, 'res_ids': res_ids, 'model': model}

    @api.model
    def get_active_records(self, single=False, msg=None, expected_model=None):
        """Return browsed records from active context.

        Args:
            single (bool): if record have to be singleton (
                default: {False}).
            msg (str): custom exception message if there is more than
                one active_id, when single=True used (default: {None})
            expected_model (str): Ensure that active model matches
                specified model.

        Returns:
            recordset

        """
        data = self.get_active_data(
            single=single, msg=msg, expected_model=expected_model
        )
        try:
            return self.env[data['model']].browse(data['res_ids'])
        except KeyError as e:
            raise ValidationError(_("Model '%s' not found.") % e)

    # O2M/M2M helpers.

    @api.model
    def get_o2m_field_for_inverse(self, inverse_name):
        """Return related o2m field using inverse_name (m2o).

        Returns first found o2m field for inverse field.

        Args:
            inverse_name (str): m2o field that is inverse field for
                target o2m field.

        Returns:
            fields.One2Many: o2m field object.

        """
        parent_model_name = self._fields[inverse_name].comodel_name
        ParentModel = self.env[parent_model_name]
        for field in ParentModel._fields.values():
            if field.type == 'one2many' and field.inverse_name == inverse_name:
                return field
        raise ValueError(
            "No one2many field found for inverse field '%s' with model '%s'"
            % (inverse_name, parent_model_name)
        )

    @api.model
    def resolve_2many_commands_to_recs(self, fname, commands, force_create=False):
        """Browse o2m/m2m commands into records.

        End result record ids is taken when browsing

        Args:
            fname (str): field name to find comodel_name.
            commands (list): commands to resolve.
            force_create (bool): whether to create records using COMMAND
            0 ({default: False}).

        Returns:
            recordset

        """

        def gather_real_ids(ids):
            return [_id for _id in ids if isinstance(_id, int)]

        def gather_create_commands(commands, count):
            create_commands = []
            for cmd in commands:
                if not count:
                    break
                if cmd[0] == 0 and cmd[1] == 0:
                    create_commands.append(cmd)
                    count -= 1
            return create_commands

        field = self._fields[fname]
        ids = field.convert_to_cache(commands, self)
        # IDs that exist in database (excluding NewId instances).
        real_ids = gather_real_ids(ids)
        RelatedModel = self.env[field.comodel_name]
        records = RelatedModel.browse(real_ids)
        if force_create:
            new_ids_count = len(ids) - len(real_ids)
            create_commands = gather_create_commands(commands, new_ids_count)
            for create_command in create_commands:
                record = RelatedModel.create(create_command[2])
                commands.remove(create_command)
                commands.append((4, record.id))
                records |= record
        return records

    def force_recompute_fields(self, fnames=None, stored_only=True):
        """Force recompute fields even if some don't need to be.

        Args:
            fnames (list[str]): custom list of compute field names. If
                None, then all computeable fields are included.
            stored_only (bool): whether to recompute only stored fields.

        """

        def get_compute_fnames(fnames):
            fnames = fnames or self._fields.keys()
            compute_fnames = []
            for fname in fnames:
                field = self._fields[fname]
                if field.compute:
                    compute_fnames.append(fname)
            if stored_only:
                return [fname for fname in compute_fnames if self._fields[fname].store]
            return compute_fnames

        if not self:
            return False
        compute_fnames = get_compute_fnames(fnames)
        if not compute_fnames:
            return False
        for fname in compute_fnames:
            self.env.add_to_compute(self._fields[fname], self)
        self.env[self._name].recompute(fnames, self)
        return True
