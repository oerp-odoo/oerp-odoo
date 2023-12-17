from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_serial_mass_produce_wizard(self):
        self.ensure_one()
        if self.picking_type_id.mass_serial_ignore_components:
            self = self.with_context(mass_serial_ignore_components=True)
        return super(MrpProduction, self).action_serial_mass_produce_wizard()

    def _check_serial_mass_produce_components(self):
        (
            have_serial_components,
            have_lot_components,
            missing_components,
            multiple_lot_components,
        ) = super()._check_serial_mass_produce_components()
        if self.env.context.get('mass_serial_ignore_components'):
            missing_components = False
        return (
            have_serial_components,
            have_lot_components,
            missing_components,
            multiple_lot_components,
        )
