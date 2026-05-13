from odoo import api, fields, models


def _is_fname_in_domain(domain, fname):
    return any(item[0] == fname for item in domain)


class OdootilHiddenMixin(models.AbstractModel):
    """Mixin to hide marked records by default.

    Similar to active field functionality if _hid_mode='full' (default).
    If _hid_mode='name_search', records would be filtered via
    name_search only.
    """

    _name = 'odootil.hidden.mixin'
    _description = "Odootil Hidden Mixin"
    _hid_mode = 'full'
    _hid_prefix = '~'
    _hid_override_name_get = True

    hid_hidden = fields.Boolean(
        string="Hidden",
        default=False,
        help="If checked, will exclude it from search if Hidden option is "
        "not explicitly included.",
    )

    @property
    def _hid_hidden_domain(self):
        return [('hid_hidden', '=', False)]

    def _is_hid_hidden_in_domain(self, domain):
        return _is_fname_in_domain(domain, 'hid_hidden')

    @api.model
    def _where_calc(self, domain, active_test=True):
        if self._hid_mode == 'full' and not self._context.get('hid_not_hide'):
            # Filter only if hid_hidden was not explicitly passed.
            if not self._is_hid_hidden_in_domain(domain):
                domain = self._hid_hidden_domain + domain
        return super()._where_calc(domain, active_test=active_test)

    # NOTE: could probably pass hid_not_hide on ir.rule:domain_get,
    # but then would need to modify it for all models, even the ones
    # that do not inherit from this, so it would not fit as a mixin
    # then.
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        # We do not want to limit access by `hid_hidden` option, we only
        # want to not search it by default.
        self = self.with_context(hid_not_hide=True)
        return super()._apply_ir_rules(query, mode=mode)

    def _filter_access_rules(self, operation):
        self = self.with_context(hid_not_hide=True)
        return super()._filter_access_rules(operation)

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        """Extend to exclude hidden records implicitly."""
        if self._hid_mode == 'name_search':
            args = args or []
            if not self._context.get(
                'hid_not_hide'
            ) and not self._is_hid_hidden_in_domain(args):
                args = self._hid_hidden_domain + args
        return super()._name_search(
            name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )

    def _hid_prepare_name(self, name):
        self.ensure_one()
        if self.hid_hidden:
            return f'{self._hid_prefix}{name}'
        return name

    def name_get(self):
        """Extend to customize hidden display name."""
        result = super().name_get()
        if self._hid_override_name_get:
            for idx, rec_id, name in enumerate(result):
                record = self.browse(rec_id)
                result[idx] = (rec_id, record._hid_prepare_name(name))
        return result
