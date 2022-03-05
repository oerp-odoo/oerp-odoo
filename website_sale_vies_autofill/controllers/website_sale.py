from odoo.http import request
from odoo import http

from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    """Extend to add method request_vies_data method."""

    @http.route(
        '/shop/vies_data/<string:vat>',
        type='json',
        auth="public",
        methods=['POST'],
        website=True,
    )
    def request_vies_data(self, vat, **kw):
        """Request vies_data from backend retrieve_vies_data method."""
        return request.env['res.partner'].sudo().retrieve_vies_data(vat)
