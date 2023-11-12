from odoo import models, fields, api


def to_names_msg(records):
    return ', '.join(records.mapped('name'))


class MrpUnbuildMultiSummary(models.TransientModel):
    _name = 'mrp.unbuild.multi.summary'
    _description = "Manufacturing Orders Multi Unbuild Summary"

    mo_unbuilt_names = fields.Text(
        "Unbuilt Manufacturing Orders", readonly=True
    )
    mo_skipped_names = fields.Text(
        "Skipped Manufacturing Orders", readonly=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        mo_unbuilt_ids = self.env.context.get('mo_unbuilt_ids')
        mo_skipped_ids = self.env.context.get('mo_skipped_ids')
        MrpProduction = self.env['mrp.production']
        if mo_unbuilt_ids:
            res['mo_unbuilt_names'] = to_names_msg(
                MrpProduction.browse(mo_unbuilt_ids)
            )
        if mo_skipped_ids:
            res['mo_skipped_names'] = to_names_msg(
                MrpProduction.browse(mo_skipped_ids)
            )
        return res
