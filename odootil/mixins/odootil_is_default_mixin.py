from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OdootilIsDefaultMixin(models.AbstractModel):
    """Mixin to add default record logic.

    Can either enforce single default or allow multiple records to be
    default (if its used in m2m relations).

    NOTE. If ``company_id`` field is defined, it assumes uniqueness per company! It
    only supports it properly when company_id is required!
    """

    _name = 'odootil.is_default.mixin'
    _description = "Odootil Is Default Mixin"
    _is_default_single = True

    is_default = fields.Boolean(copy=False)

    @api.model
    def is_default_get(self, **kw):
        domain = self._is_default_prepare_domain(**kw)
        return self.search(domain)

    @api.model
    def is_default_prepare_check_deps(self):
        deps = ['is_default']
        if 'company_id' in self._fields:
            deps.append('company_id')
        if 'active' in self._fields:
            deps.append('active')
        return deps

    @api.constrains(is_default_prepare_check_deps)
    def _check_is_default(self):
        if not self._is_default_single:
            return
        kw = {}
        msg = _("Only single '%s' can be default!", self._description)
        if 'company_id' in self._fields:
            kw['company_id'] = self.env.company.id
            # A bit redundant..
            msg = _("Only single '%s' can be default per company!", self._description)
        if len(self.is_default_get(**kw)) > 1:
            raise ValidationError(msg)

    @api.model
    def _is_default_prepare_domain(self, **kw):
        domain = [('is_default', '=', True)]
        if 'company_id' in self._fields:
            try:
                domain.append(('company_id', '=', kw['company_id']))
            except KeyError:
                raise ValidationError(
                    _(
                        "Programming error: 'company_id' is expected as kw when "
                        + "using _is_default_prepare_domain for records that have "
                        + "'company_id' field!"
                    )
                )
        return domain
