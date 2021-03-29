from footil.formatting import get_formatted_exception

from odoo.exceptions import ValidationError
from odoo import models, fields, _


class DeliveryTrackingLink(models.Model):
    """Model to specify custom tracking link formats."""

    _name = 'delivery.tracking.link'
    _description = "Delivery Tracking Link"

    name = fields.Char(required=True)
    url_format = fields.Char(
        required=True,
        string="URL Format",
        help="At minimum should use `picking.carrier_tracking_ref` to combine"
        " URL with tracking number. E.g. "
        "`https://some-domain.com/tracking/{picking.carrier_tracking_ref}`"
    )

    def generate_link(self, picking):
        """Generate tracking link using URL and picking object data."""
        self.ensure_one()
        try:
            return self.url_format.format(picking=picking)
        except Exception:
            raise ValidationError(
                _("Tracking Links has incorrect format. Error:\n%s") %
                get_formatted_exception()
            )
