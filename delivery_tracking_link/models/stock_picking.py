from odoo import api, fields, models


class StockPicking(models.Model):
    """Extend to add field carrier_tracking_url_custom."""

    _inherit = 'stock.picking'

    # TODO: should we validate if correct schema is used here?
    carrier_tracking_url_custom = fields.Char(
        "Custom Tracking URL",
        help="If set, will use this URL for tracking, instead of carrier "
        + "generated one",
    )

    @api.depends('carrier_id', 'carrier_tracking_ref', 'carrier_tracking_url_custom')
    def _compute_carrier_tracking_url(self):
        super()._compute_carrier_tracking_url()
        for picking in self:
            if picking.carrier_tracking_url_custom:
                picking.carrier_tracking_url = picking.carrier_tracking_url_custom
