from odoo import fields, models

from ..const import CFG_PARAM_NO_INVOICE_MATCHING


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_no_invoice_matching = fields.Boolean(
        "No Vendor Bills Matching", config_parameter=CFG_PARAM_NO_INVOICE_MATCHING
    )
