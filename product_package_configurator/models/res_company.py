from odoo import fields, models

from .. import const


class ResCompany(models.Model):

    _inherit = 'res.company'

    package_default_global_box_extra = fields.Float(
        string="Default Global Box Extra",
        default=const.DEFAUL_GLOBAL_BOX_EXTRA,
    )
    package_default_lid_extra = fields.Float(
        string="Default Lid Extra",
        default=const.DEFAULT_LID_EXTRA,
    )
    package_default_outside_wrapping_extra = fields.Float(
        string="Default Outside Wrapping Extra",
        default=const.DEFAULT_OUTSIDE_WRAPPING_EXTRA,
    )
