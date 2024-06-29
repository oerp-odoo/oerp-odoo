from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SharepointSite(models.Model):
    """Model about sharepoint site and how to communicate with it."""

    _name = 'sharepoint.site'
    _description = "Sharepoint Site"
    _rec_name = 'hostname'

    state = fields.Selection(
        [('draft', "Draft"), ('confirm', "Confirmed"), ('cancel', "Cancelled")],
        required=True,
        default='draft',
        copy=False,
        readonly=True,
    )
    auth_id = fields.Many2one(
        'sharepoint.auth',
        required=True,
        states={"confirm": [("readonly", True)]},
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda s: s.env.company,
        states={"confirm": [("readonly", True)]},
    )
    hostname = fields.Char(
        help="Should be entered without https://",
        states={"confirm": [("readonly", True)]},
    )
    # TODO: implement paths cleanup logic. We should enforce /a/b paths
    # even if let say it specifies /a/b/ or a/b or a/b/
    site_rel_path = fields.Char(
        "Site Relative Path",
        help="Root path of drive. For example /sites/Mysite. Used to discover Site ID",
        states={"confirm": [("readonly", True)]},
    )
    site_id = fields.Char(
        "Site ID",
        help="Sharepoint Site ID to use. Can be entered manually. "
        + "If not it will be discovered by Site Relative Path",
        states={"confirm": [("readonly", True)]},
    )
    drive_id = fields.Char(
        "Drive ID",
        help="Can be entered manually. Otherwise default Drive ID will be discovered.",
        states={"confirm": [("readonly", True)]},
    )

    @api.constrains('state', 'company_id')
    def _check_company_id(self):
        for site in self:
            if site.state == 'confirm' and self.search(
                [
                    ('state', '=', 'confirm'),
                    ('company_id', '=', site.company_id.id),
                    ('id', '!=', site.id),
                ],
                limit=1,
            ):
                # TODO: support more than one site per company! We could have some
                # extra identifier to know when each site should be used.
                raise ValidationError(_("Confirmed Site must be unique per company!"))

    def action_setup_missing(self):
        """Set up missing data for site.

        site_id and/or drive_id is discovered and set if its not
        set already.
        """
        self.ensure_one()
        data = self.discover_site_data()
        if data:
            self.write(data)
        return True

    def discover_site_data(self):
        self.ensure_one()
        self._validate_discovery_prerequisites()
        data = {}
        SharepointApi = self.env['sharepoint.api']
        if not self.site_id:
            data['site_id'] = SharepointApi.get_site_id(
                self.hostname, self.site_rel_path, options={'auth': self.auth_id}
            )
        if not self.drive_id:
            site_id = self.site_id or data['site_id']
            data['drive_id'] = SharepointApi.get_default_drive_id(
                site_id, options={'auth': self.auth_id}
            )
        return data

    def action_confirm(self):
        self.ensure_one()
        self._validate_confirm()
        self.state = 'confirm'

    def action_to_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancel'

    def get_site(self, company, raise_not_found=False, **kw):
        site = self.search(self.prepare_site_domain(company, **kw), limit=1)
        if not site and raise_not_found:
            raise ValidationError(
                _("Sharepoint Site Not Found. Make sure it is configured properly!")
            )
        return site

    def prepare_site_domain(self, company, **kw):
        """Prepare domain to get sharepoint.site record."""
        return [
            ('state', '=', 'confirm'),
            ('company_id', '=', company.id),
        ]

    def _validate_discovery_prerequisites(self):
        self.ensure_one()
        if not self.site_id and not self.site_rel_path:
            raise ValidationError(
                _("Site Relative Path is needed to discover Site ID!")
            )

    def _validate_confirm(self):
        self.ensure_one()
        if not self.site_id:
            raise ValidationError(_("Site ID must be set to confirm site!"))
        if not self.drive_id:
            raise ValidationError(_("Drive ID must be set to confirm site!"))
