import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class MrpUnbuildMulti(models.TransientModel):
    """Wizard to handle multiple MO unbuilds."""

    _name = 'mrp.unbuild.multi'
    _description = "Manufacturing Orders Multi Unbuild"

    unbuild_type = fields.Selection(
        [('all', "All Quantities")],
        default='all',
        required=True,
    )
    mrp_production_ids = fields.Many2many(
        'mrp.production',
        'unbuild_multi_production_rel',
        'multi_id',
        'production_id',
        string="Manufacturing Orders",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ids = self.env.context.get('active_ids')
        if ids and self.env.context.get('active_model') == 'mrp.production':
            res['mrp_production_ids'] = [(6, 0, ids)]
        return res

    def action_unbuild_multi(self):
        self.ensure_one()
        self._validate_mos()
        mos_unbuild, mos_skipped = self._find_mos()
        unbuilds = self._create_unbuilds(mos_unbuild)
        for unbuild in unbuilds:
            res = unbuild.action_validate()
            if res is not True:
                mo = unbuild.mo_id
                mos_skipped |= unbuild.mo_id
                mos_unbuild -= mo
        _logger.info(
            "Manufacturing Orders (%s) already have unbuild (or "
            + "insufficient quantity). Skipping",
            ', '.join(mos_skipped.mapped('name')),
        )
        view_id = self.env.ref(
            'mrp_unbuild_multi.mrp_unbuild_multi_summary_view_form'
        ).id
        return {
            'name': _('Multi Unbuild Summary'),
            'view_mode': 'form',
            'res_model': 'mrp.unbuild.multi.summary',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': {
                'mo_unbuilt_ids': mos_unbuild.ids,
                'mo_skipped_ids': mos_skipped.ids,
            },
            'target': 'new',
        }

    def _validate_mos(self):
        self.ensure_one()
        non_done_mos = self.mrp_production_ids.filtered(
            lambda r: r.state != 'done'
        )
        if non_done_mos:
            raise ValidationError(
                _(
                    "To unbuild, all manufacturing orders must be in done "
                    + "state. Incorrect ones: %s",
                    ', '.join(non_done_mos.mapped('name')),
                )
            )

    def _common_prepare_unbuild(self, mo):
        self.ensure_one()
        vals = {
            'product_id': mo.product_id.id,
            'product_uom_id': mo.product_uom_id.id,
            'mo_id': mo.id,
            'company_id': mo.company_id.id,
            'location_id': mo.location_dest_id.id,
            'location_dest_id': mo.location_src_id.id,
        }
        if mo.lot_producing_id:
            vals['lot_id'] = mo.lot_producing_id.id
        return vals

    def _prepare_unbuild_all(self, mo):
        self.ensure_one()
        return {'product_qty': mo.qty_produced}

    def _find_mos(self):
        self.ensure_one()
        mos = self.mrp_production_ids
        mos_skipped = (
            self.env['mrp.unbuild']
            .search([('mo_id', 'in', mos.ids)])
            .mapped('mo_id')
        )
        return (mos - mos_skipped, mos_skipped)

    def _create_unbuilds(self, mos):
        self.ensure_one()
        prepare_method = getattr(self, f'_prepare_unbuild_{self.unbuild_type}')
        vals_list = []
        for mo in mos:
            vals = self._common_prepare_unbuild(mo)
            vals.update(prepare_method(mo))
            vals_list.append(vals)
        return self.env['mrp.unbuild'].create(vals_list)
