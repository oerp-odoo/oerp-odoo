from odoo import fields, models

CFG_PARAM_PO_AUTO_DONE = 'purchase_auto_done.use'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_purchase_auto_done = fields.Boolean(
        "Auto Lock Purchase Orders", config_parameter=CFG_PARAM_PO_AUTO_DONE
    )
