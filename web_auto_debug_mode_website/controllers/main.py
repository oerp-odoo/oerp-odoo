from odoo.http import request
from odoo import http
from odoo.addons.website.controllers.main import Website


class WebsiteExtended(Website):
    """Extended to prevent website from forcing /web redirect."""

    @http.route()
    def web_login(self, redirect=None, **kw):
        """Override so website module won't force hardcoded /web."""
        response = super(WebsiteExtended, self).web_login(
            redirect=redirect, **kw)
        # Only valid for successfully logged in backend users.
        if (not redirect and request.params['login_success'] and
            request.env['res.users'].browse(
                request.uid).has_group('base.group_user')):
            redirect = self._login_redirect(request.uid, redirect=redirect)
            return http.redirect_with_hash(redirect)
        return response
