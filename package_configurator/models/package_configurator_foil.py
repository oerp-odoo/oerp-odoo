from odoo import fields, models

from .. import const


class PackageConfiguratorFoil(models.Model):
    _name = 'package.configurator.foil'
    _description = "Package Configurator Foil"

    configurator_id = fields.Many2one(
        'package.configurator', required=True, ondelete='cascade'
    )
    component_id = fields.Many2one(
        'package.configurator.component',
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
