from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain

from odoo.addons.odootil.tools.file import load_py_attribute

from ..utils import check_url
from ..value_objects.profile import ProfileFilter


class HttpClientProfile(models.Model):
    _name = 'http.client.profile'
    _description = "HTTP Client Connection"

    name = fields.Char(required=True)
    base_url = fields.Char("Base URL", required=True, help="Base URL for endpoints")
    auth_id = fields.Many2one('http.client.auth', required=True)
    active = fields.Boolean(default=True)
    retry_id = fields.Many2one('http.client.retry', string="Retry Strategy")
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company)
    integration = fields.Selection([])
    non_ok_exception_path = fields.Char(
        "Exception Path for Not OK Response",
        help="Dotted path of an exception to raise if response is not OK. If empty, "
        + "error is only logged, but not raised.",
    )

    @api.constrains('base_url')
    def _check_base_url(self):
        if self.env.context.get('http_client_skip_check_base_url'):
            return
        for conn in self:
            check_url(self.env, conn.base_url)

    @api.constrains('non_ok_exception_path')
    def _check_non_ok_exception_path(self):
        for rec in self.filtered('non_ok_exception_path'):
            try:
                rec.load_non_ok_exception()
            except Exception as e:
                raise ValidationError(
                    self.env._("Incorrect Exception path. Error: %s", e)
                )

    def get_profile(self, profile_filter: ProfileFilter):
        profile = self.find_profiles(profile_filter)
        if not profile:
            raise ValidationError(
                self.env._("No profile found matching filter: %s", profile_filter)
            )
        if len(profile) > 1:
            raise ValidationError(
                self.env._(
                    "More than one profile %(conns)s found matching "
                    "filter: %(profile_filter)s",
                    conns=', '.join(profile.mapped('name')),
                    profile_filter=profile_filter,
                )
            )
        return profile

    def load_non_ok_exception(self):
        self.ensure_one()
        return load_py_attribute(self.non_ok_exception_path)

    def find_profiles(self, profile_filter: ProfileFilter):
        domain = self._prepare_domain(profile_filter)
        return self.search(domain)

    def _prepare_domain(self, profile_filter: ProfileFilter) -> Domain:
        if profile_filter.company_id:
            domain = Domain('company_id', '=', profile_filter.company_id)
        else:
            # Even if company_id is not passed in filter, we should still limit
            # to user's company or global ones only!
            domain = Domain('company_id', '=', self.env.company.id) | Domain(
                'company_id', '=', False
            )
        if profile_filter.integration:
            domain &= Domain('integration', '=', profile_filter.integration)
        return domain
