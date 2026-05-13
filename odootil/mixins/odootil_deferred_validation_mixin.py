from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from odoo import models


@dataclass(frozen=True)
class DeferredValidationSpec:
    condition_fields: frozenset[str]
    excluded_fields: frozenset[str]


class OdootilDeferredValidationMixin(models.AbstractModel):
    """Mixin to trigger constrains after all related fields were set.

    This is useful in cases when multiple fields are involved in
    constraint and multiple such fields are also related. In standard
    odoo related fields are updated one by one, so some constraints can
    fail, when expectation is to validate after all related fields were
    updated instead of one by one.
    """

    _name = 'odootil.deferred.validation.mixin'
    _description = "Deferred Validation Mixin"

    @property
    def deferred_validation_spec_class(self):
        return DeferredValidationSpec

    @property
    def deferred_validation_spec_map(self):
        """Return deferred validation conditions map.

        This map specifies target rel path (
            my_field_id or my_field_id.my_other_field_id
        )
        field to deffer validations on and which fields are involved:

        - condition_fields: specify which fields must be present in vals
          to trigger deferred validation.
        - excluded_fields: specify which fields will be excluded from
          validation.

        Example:
            {
                'related_field_id': [
                    DeferredValidationFieldsSpec(
                        condition_fields=frozenset(['f1', 'f2'])
                        excluded_fields=frozenset(['f1', 'f2'])
                    )
                ]
            }

        """
        raise NotImplementedError()

    # TODO: handle for create too!
    def write(self, vals):
        exclusion_map = self._deferred_validation_prepare_exclusion_map(vals)
        if not exclusion_map:
            return super().write(vals)
        # Send signal to defer validations.
        res = super(
            OdootilDeferredValidationMixin,
            self.with_context(deferred_validation_exclusion_map=exclusion_map),
        ).write(vals)
        # Trigger deferred validations now!
        for rel_recs, excluded_fields in exclusion_map.items():
            rel_recs._validate_fields(excluded_fields)
        return res

    def _deferred_validation_prepare_exclusion_map(self, vals):
        map_ = defaultdict(set)
        for rel_field_path, specs in self.deferred_validation_spec_map.items():
            rel_recs = self.mapped(rel_field_path)
            if not rel_recs:
                continue
            for spec in specs:
                if spec.condition_fields.issubset(vals):
                    map_[rel_recs] |= spec.excluded_fields
        return map_
