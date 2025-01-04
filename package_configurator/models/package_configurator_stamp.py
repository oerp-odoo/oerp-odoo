from odoo import fields, models

from .. import const


class PackageConfiguratorStamp(models.Model):
    _name = 'package.configurator.stamp'
    _description = "Package Configurator Stamp"

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
    stamp_id = fields.Many2one('package.stamp', required=True)
