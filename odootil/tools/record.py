"""Recordset helpers module."""

from collections import defaultdict

from footil.xtyping import is_string

from odoo.exceptions import ValidationError


def cleanup_noop_values(records, vals: dict):
    """Remove keys from dictionary if it would update to the already existing value."""
    if not records or not vals:
        return None
    # Note. If at least one record has no noop values, then we don't
    # cleanup at all, even if some records have it!
    candidates = []
    for record, new_record in zip(records, records.new_multi(values=vals)):
        candidates.append({k: v for k, v in vals.items() if new_record[k] != record[k]})
    # Candidate must be exactly the same on all records to be a match!
    candidate = candidates[0]
    if not all(c == candidates[0] for c in candidates):
        return None
    keys_to_clean = set(vals.keys()) - set(candidate.keys())
    for key in keys_to_clean:
        vals.pop(key)


def get_record_id_by_domain(Model, domain, limit=None, raise_not_found=True):
    _ = Model.env._
    record = Model.search(domain, limit=limit)
    if not record:
        if raise_not_found:
            description = Model._description
            raise ValidationError(_(f"No {description} found using domain {domain}"))
        return None
    if len(record) > 1:
        raise ValidationError(
            _(f"Found more than one record ({Model._name}) using domain {domain}")
        )
    return record.id


def get_record_id_by_name(
    Model, name, limit=None, caseless=False, force_create=False, raise_not_found=True
):
    if force_create:
        raise_not_found = False
    record_id = get_record_id_by_domain(
        Model,
        [('name', '=ilike' if caseless else '=', name)],
        limit=limit,
        raise_not_found=raise_not_found,
    )
    if record_id is None and force_create:
        # Attempt to create by name
        try:
            record_id = Model.create({'name': name}).id
        except Exception as e:
            raise ValidationError(
                Model.env._(
                    "Could not create record for %(model_name) using name %(name)s."
                    + " Error: %(e)s",
                    model_name=Model._name,
                    name=name,
                    e=e,
                )
            )
    return record_id


def get_partner_id_by_vat(env, vat: str):
    # Forcing limit, to make search faster. Though we must be sure
    # VAT uniqueness is guaranteed.
    company_id = env.user.company_id.id
    return get_record_id_by_domain(
        env['res.partner'],
        domain=[('vat', '=', vat), ('company_id', 'in', (False, company_id))],
        limit=1,
    )


def validate_record_exists(record, msg=None, raise_err=True):
    if not msg:
        msg = record.env._(
            "%(description)s with ID %(record_id)s does not exist",
            description=record._description,
            record_id=record.id,
        )
    if not record.exists() or hasattr(record, 'active') and not record.active:
        if raise_err:
            raise ValidationError(msg)
        return msg
    # From outside, if it tries to access record outside that user companies,
    # it means it can't.
    if hasattr(record, 'company_id'):
        if record.company_id and record.company_id not in record.env.companies:
            if raise_err:
                raise ValidationError(msg)
            return msg
    return ''


def get_record_by_xmlid(env, xmlid, msg):
    try:
        record = env.ref(xmlid)
    except ValueError:
        raise ValidationError(msg)
    validate_record_exists(record, msg=msg)
    return record


class RecordChangeTracker:
    """Class to track wanted recordset field value changes.

    When tracker is initiated with given recordset, it saves specified
    field keys state. When change method is called and if any tracked
    field values were changed, it will return grouped changed fields
    with their records.

    If record is unlinked in a meantime, its tracking will be lost and
    will not show any changes for it.
    """

    def __init__(self, records, spec):
        """Initiate to track recordset by specified fields.

        Args:
            records (recordset): recordset to track.
            spec (sequence): list of field names to track. Item can
                also be tuple where first item is field name and second,
                function with record as an argument. Function is used
                to limit changes tracking by some specific values.

        """
        self._Model = records.env[records._name]
        self._fields = tuple(self._spec_to_fields(spec))
        self._field_conditions = self._spec_to_conditions(spec)
        self._state = None
        self._record_ids = None
        self._save(records)

    @property
    def fields(self):
        """Return related field names that are tracked."""
        return self._fields

    @property
    def records(self):
        """Return newly browsed recordset from record_ids."""
        return self._Model.browse(self._record_ids).exists()

    def _spec_to_fields(self, spec):
        return [item if is_string(item) else item[0] for item in spec]

    def _spec_to_conditions(self, spec):
        def passing_condition(record):
            return True

        conditions = {}
        for item in spec:
            if is_string(item):
                conditions[item] = passing_condition
            else:
                conditions[item[0]] = item[1]
        return conditions

    def _read_record_state(self, record):
        state = {}
        _fields_spec = self._Model._fields
        for fname in self._fields:
            if _fields_spec[fname].type in (
                'many2one',
                'many2many',
                'one2many',
            ):
                state[fname] = tuple(sorted(record[fname].ids))
            else:
                state[fname] = record[fname]
        return state

    def _read(self, records):
        for record in records:
            yield (record, self._read_record_state(record))

    def _save(self, records):
        self._record_ids = records.ids
        # Reset state, so we would not leave unlinked records.
        self._state = {}
        for record, record_state in self._read(records):
            self._state[record.id] = record_state

    def save(self):
        """Save existing recordset state."""
        self._save(self.records)

    def _compare_state(self):
        """Compare state and yield records with metadata if changed."""
        for record, record_state in self._read(self.records):
            saved_record_state = self._state[record.id]
            for fname, value in record_state.items():
                condition = self._field_conditions[fname]
                # Compare if state changed.
                if saved_record_state[fname] != value and condition(record):
                    yield (record, fname, value)

    def compute_change_any(self):
        """Return combined recs if any of their tracked vals changed.

        Returns:
            recordset

        """
        records = self._Model.env[self._Model._name]
        for record, __, __ in self._compare_state():
            records |= record
        return records

    def compute_change_fields(self):
        """Return changes by fields separately.

        Change format is detailed up to fields:
            {
                'fname1': recordset1,
                'fname2': recordset2,
                ...
            }
        """
        changes = defaultdict(lambda: self._Model)
        for record, fname, __ in self._compare_state():
            changes[fname] |= record
        return changes

    def compute_change_groups(self):
        """Return changes grouped by fields.

        Key field names grouping is done following specified spec order.

        Change format is detailed up to fields:
            {
                frozenset({'fname1'}): recordset1,
                frozenset({'fname2', 'fname3'}): recordset2,
                frozenset({'fname4'}): recordset3,
                frozenset({'fname5', 'fname6'}): recordset4,
                ...
            }
        """
        changes = defaultdict(lambda: self._Model)
        fnames_by_record = defaultdict(set)
        # Generate set of field names which changed for specific record.
        for record, fname, __ in self._compare_state():
            fnames_by_record[record].add(fname)
        # Use set of field names as a key. We don't care about key items
        # order, so using frozenset for that.
        for record, fnames in fnames_by_record.items():
            changes[frozenset(fnames)] |= record
        return changes

    def compute_change_values(self):
        """Return changes comparing saved state and current state.

        Change format is detailed up to field values:
            {
                'fname1': {
                    'records': recordset,
                    'by_value': {
                        val1: recordset,
                        val2: recordset,
                        ...
                    }
                }
                ...
            }
        """
        changes = defaultdict(dict)
        for record, fname, value in self._compare_state():
            field_state = changes[fname]
            field_state.setdefault('records', self._Model)
            field_state.setdefault('by_value', defaultdict(lambda: self._Model))
            # Groups all records that have field changed to
            # any value.
            field_state['records'] |= record
            field_state['by_value'][value] |= record
        return changes
