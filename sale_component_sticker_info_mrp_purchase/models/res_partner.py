from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # For components sticker info.
    components_doc_receiver = fields.Boolean(
        "Components Document Receiver",
        help="Components Info email will be sent to this partner when related PO"
        + " is confirmed",
    )
