import json
from collections import defaultdict

from lxml import etree

from odoo import api, models

from ..tools.decor import no_noop_write


# NOTE: currently supports single sync map per model
class OdootilFieldsSync(models.AbstractModel):
    """Model for fields sync to target model via related target field."""

    _name = 'odootil.fields_sync'
    _description = "Odootil Fields Sync"

    @property
    def fields_sync_fields_loose(self):
        """List of field names to be synced.

        Fields in this list will be synced on target record only if
        field value is not set on target record or old values match on
        both - source and target record.

        NOTE. Assuming that all field names match between synced models.
        """
        return []

    @property
    def fields_sync_fields_forced(self):
        """List of field names to be forced synced.

        Fields in this list will be forced to sync on target record
        regardless of what values are already set on target record.

        NOTE. Assuming that all field names match between synced models.
        """
        return []

    @property
    def fields_sync_fields_forced_modifiers_exceptions(self):
        """List of field names excepted while applying modifiers.

        Modifiers wont be applied on provided fields.
        """
        return []

    @property
    def fields_sync_fields_forced_modifiers(self):
        """Fields view modifiers for forced synced fields."""
        return {}

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        """Extend to apply modifiers on forced synced fields."""
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if self.fields_sync_fields_forced_modifiers and view_type in ('tree', 'form'):
            doc = etree.XML(res['arch'])
            for field in res['fields']:
                if field in self.fields_sync_fields_forced_modifiers_exceptions:
                    continue
                if field in self.fields_sync_fields_forced:
                    for node in doc.xpath(f"//field[@name='{field}']"):
                        modifiers = json.loads(node.get("modifiers", '{}'))  # -> str
                        modifiers.update(self.fields_sync_fields_forced_modifiers)
                        node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @property
    def fields_sync_target_field(self):
        """Name of the target field to sync fields through.

        NOTE. Assuming origin and target models has a direct relation.
        """
        raise NotImplementedError

    @property
    def fields_sync_target_model_name(self):
        """Name of the target model to sync on."""
        raise NotImplementedError

    @property
    def fields_sync_conditions_map(self):
        """Conditions that must pass for sync to apply for fields.

        Map keys are field names as tuple that must have a condition.
        Value is a function that has two arguments: rec and target_rec
        where rec is record that syncing is happening from and
        target_rec is record that syncing is done to.

        If multiple field names are added in key, it means each of
        them have same condition.

        E.g. {('fname1',): lambda rec, target_rec: target_rec.code != 'a'}
        """
        return {}

    def fields_sync_prepare_sync_data(self, vals):
        # Sync only if any of sync fields are changed.
        fields_to_sync = set(
            self.fields_sync_fields_loose + self.fields_sync_fields_forced
        ) & set(vals)
        if not fields_to_sync:
            return {}
        matches = self._fields_sync_match_target_with_sync_fields(fields_to_sync)
        return self._fields_sync_merge_matched_sync_fields(matches)

    @no_noop_write
    def write(self, vals):
        # Must prep before super, so we know what are current values.
        rec_groups = self.fields_sync_prepare_sync_data(vals)
        res = super().write(vals)
        self.fields_sync_sync(vals, rec_groups)
        return res

    def fields_sync_sync(self, vals, groups):
        """Sync some fields to target model via target field.

        Fields are only synced downstream (from current object to
        target object) and only if either downstream fields are not
        set or match with current respective object's field values.

        Args:
            vals (dict): current object values.
            groups (dict): grouped target object (by common field names)
                to sync.

        """
        # Sync matching data.
        for fnames, recs in groups.items():
            rec_vals = {fname: vals[fname] for fname in fnames}
            recs.write(rec_vals)

    def _fields_sync_match_target_with_sync_fields(self, fields_to_sync):
        """Create dictionary to map each record (key) with matching sync fields."""
        matches = defaultdict(set)
        for src_rec in self:
            for target_rec in src_rec[self.fields_sync_target_field]:
                for sync_field in fields_to_sync:
                    if not self._fields_sync_check_sync_field(
                        src_rec, target_rec, sync_field
                    ):
                        continue
                    matches[target_rec].add(sync_field)
        return matches

    def _fields_sync_merge_matched_sync_fields(self, matches: dict):
        """Merge matching sync_fields between records.

        Records are merged if their values match.

        matches keys (records) are swapped with values (sync fields)
        to form dictionary of:
            {
                frozenset(['a', 'b', 'c']): recordset1,
                frozenset(['c']): recordset2,
                frozenset(['c', 'd']): recordset3,
                ...
                ...
            }
        """
        groups = defaultdict(lambda: self.env[self.fields_sync_target_model_name])
        for target_rec, sync_fields in matches.items():
            groups[frozenset(sync_fields)] |= target_rec
        return groups

    def _fields_sync_check_sync_field(self, src_rec, target_rec, sync_field):
        if not self._fields_sync_check_conditions_map(src_rec, target_rec, sync_field):
            return False
        # Check if sync is forced
        if sync_field in self.fields_sync_fields_forced:
            return True
        # Check if sync_field is empty or match exactly
        return (
            not target_rec[sync_field] or src_rec[sync_field] == target_rec[sync_field]
        )

    def _fields_sync_check_conditions_map(self, src_rec, target_rec, sync_field):
        def match_condition(fname, conditions_map):
            for fnames, condition in conditions_map.items():
                if fname in fnames:
                    return condition
            return None

        conditions_map = self.fields_sync_conditions_map
        # Nothing to check
        if not conditions_map:
            return True
        condition = match_condition(sync_field, conditions_map)
        return condition is None or condition(src_rec, target_rec)
