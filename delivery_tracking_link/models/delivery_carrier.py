from odoo import fields, models


class DeliveryCarrier(models.Model):
    """Extend to implement delivery.tracking.link as custom links."""

    _inherit = 'delivery.carrier'

    tracking_link_id = fields.Many2one('delivery.tracking.link')
    # Rename standard field to not clash with tracking_link_id.
    tracking_url = fields.Char(string="Tracking URL")

    def get_tracking_link(self, picking):
        """Extend to use tracking_link_id for simple delivery_type.

        Simple delivery types: fixed, base_on_rule.
        """
        link = super().get_tracking_link(picking)
        if (
            not link
            and self.tracking_link_id
            and self.delivery_type in ('fixed', 'base_on_rule')
        ):
            return self.tracking_link_id.generate_link(picking)
        return link
