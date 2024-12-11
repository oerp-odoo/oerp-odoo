from odoo import fields, models

from .. import const


class PackageConfiguratorBoxFoil(models.Model):
    _name = 'package.configurator.box.foil'
    _description = "Package Configurator Box Foil"

    configurator_id = fields.Many2one(
        'package.configurator.box', required=True, ondelete='cascade'
    )
    component_id = fields.Many2one(
        'package.configurator.box.component',
        required=True,
        domain="[('configurator_id', '=', configurator_id)]",
        ondelete='cascade',
    )
    side = fields.Selection(
        const.COMPONENT_SIDE_SELECTION,
        default=const.ComponentSide.INSIDE,
        required=True,
    )
    foil_id = fields.Many2one('package.foil', required=True)
