from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PackageConfigurator(models.Model):
    _name = 'package.configurator'
    _description = "Package Configurator"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if res.get('company_id'):
            company = self.env['res.company'].browse(res['company_id'])
        else:
            company = self.env.company
        if 'lid_extra' in default_fields:
            res['lid_extra'] = company.package_default_lid_extra
        if 'outside_wrapping_extra' in default_fields:
            res[
                'outside_wrapping_extra'
            ] = company.package_default_outside_wrapping_extra
        return res

    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done")],
        default="draft",
        required=True,
    )
    base_length = fields.Float(required=True)
    base_width = fields.Float(required=True)
    base_height = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    description_warnings = fields.Html(compute='_compute_description_warnings')
    currency_id = fields.Many2one(related='company_id.currency_id')
    circulation_ids = fields.One2many(
        comodel_name='package.configurator.circulation',
        inverse_name='configurator_id',
        string="Circulations",
    )
    component_ids = fields.One2many(
        comodel_name='package.configurator.component',
        inverse_name='configurator_id',
        string="Components",
    )
    cfg_stamp_ids = fields.One2many(
        comodel_name='package.configurator.stamp',
        inverse_name='configurator_id',
        string="Stamps",
    )
    cfg_foil_ids = fields.One2many(
        comodel_name='package.configurator.foil',
        inverse_name='configurator_id',
        string="Foils",
    )
    cfg_lamination_ids = fields.One2many(
        comodel_name='package.configurator.lamination',
        inverse_name='configurator_id',
        string="Laminations",
    )
    lid_height = fields.Float(required=True)
    lid_extra = fields.Float()
    outside_wrapping_extra = fields.Float()
    box_type_id = fields.Many2one('package.box.type', required=True)
    print_house_id = fields.Many2one('package.print.house')

    @api.depends(
        'base_length',
        'base_width',
        'base_height',
        'box_type_id',
        'lid_height',
        'component_ids.sheet_id',
        'component_ids.fit_qty',
        'component_ids.component_type',
    )
    def _compute_description_warnings(self):
        for rec in self:
            rec.description_warnings = self.env[
                'package.warning'
            ].get_formatted_warnings(self)

    @api.onchange('box_type_id')
    def _onchange_box_type_id(self):
        if self.box_type_id.default_component_ids and not self.component_ids:
            PackageComponent = self.env['package.configurator.component']
            for default_comp in self.box_type_id.default_component_ids:
                self.component_ids |= PackageComponent.new(
                    {'component_type': default_comp.component_type}
                )

    @api.constrains(
        'box_type_id',
        'base_length',
        'base_width',
        'base_height',
    )
    def _check_dimensions(self):
        def get_msg(name, dim_type, min_amount):
            return _(
                "Minimum box (%(name)s) %(dim_type)s is %(min_amount)s",
                name=name,
                dim_type=dim_type,
                min_amount=min_amount,
            )

        for box in self:
            res = box.box_type_id.validate_dimensions(
                box.base_length, box.base_width, box.base_height
            )
            box_type = box.box_type_id
            name = box_type.name
            if not res['length']:
                raise ValidationError(get_msg(name, _("length"), box_type.min_length))
            if not res['width']:
                raise ValidationError(get_msg(name, _("width"), box_type.min_width))
            if not res['height']:
                raise ValidationError(get_msg(name, _("height"), box_type.min_height))

    def action_setup(self):
        """Create/recreate setup records for each circulation."""
        self.ensure_one()
        return self.circulation_ids.create_circulation_setups(self._find_box_setups())

    def _find_box_setups(self):
        self.ensure_one()
        domain = self._prepare_box_setups_domain()
        return self.env['package.box.setup'].search(domain)

    def _prepare_box_setups_domain(self):
        self.ensure_one()
        return [('company_id', '=', self.company_id.id)]
