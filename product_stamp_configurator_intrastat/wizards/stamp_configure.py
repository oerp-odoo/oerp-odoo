from odoo import api, fields, models


class StampConfigure(models.TransientModel):
    """Extend to integrate with intrastat."""

    _inherit = 'stamp.configure'

    intrastat_code_id = fields.Many2one(
        'account.intrastat.code', string="Commodity Code"
    )

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        intrastat_code_id = self.env.company.intrastat_stamp_default_code_id.id
        if 'intrastat_code_id' in default_fields and intrastat_code_id:
            res['intrastat_code_id'] = intrastat_code_id
        return res

    def _prepare_common_product_vals(self):
        res = super()._prepare_common_product_vals()
        intrastat_code_id = self.intrastat_code_id.id
        if intrastat_code_id:
            res['intrastat_code_id'] = intrastat_code_id
        return res
