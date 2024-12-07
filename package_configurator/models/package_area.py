from odoo import api, fields, models


class PackageArea(models.Model):
    _name = 'package.area'
    _description = "Package Area"

    def _get_uom_categ_length_id(self):
        return self.env.ref('uom.uom_categ_length').id

    name = fields.Char(compute='_compute_name', store=True)
    pa_length = fields.Float(string="Length", required=True)
    pa_width = fields.Float(string="Width", required=True)
    # Hack to force only specific types of UoMs!
    uom_categ_length_id = fields.Integer(
        compute='_compute_uom_categ_length_id', default=_get_uom_categ_length_id
    )
    uom_id = fields.Many2one('uom.uom', required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    @api.depends('pa_length', 'pa_width', 'uom_id')
    def _compute_name(self):
        for rec in self:
            area = rec.pa_length * rec.pa_width
            rec.name = f"{area:2g}{rec.uom_id.name}²"

    def _compute_uom_categ_length_id(self):
        self.update({'uom_categ_length_id': self._get_uom_categ_length_id()})
