from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from .. import const
from ..utils.search import search_record_by_context_key


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

    @api.model
    def _get_default_package_type_id(self):
        return search_record_by_context_key(
            self.env['package.type'], 'package_type_code'
        )

    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done")],
        default="draft",
        required=True,
    )
    package_type_id = fields.Many2one(
        'package.type', required=True, default=_get_default_package_type_id
    )
    package_type_code = fields.Selection(related='package_type_id.code')
    package_kind_id = fields.Many2one(
        'package.kind',
        required=True,
        domain="[('package_type_id', '=', package_type_id)]",
    )
    configurator_box_id = fields.Many2one(
        'package.configurator',
        string="Box",
        domain=[('package_type_id.code', '=', const.PackageType.BOX)],
    )
    configurator_insert_ids = fields.One2many(
        'package.configurator', 'configurator_box_id', string="Inserts"
    )
    configurator_insert_count = fields.Integer(
        compute='_compute_configurator_insert_count'
    )
    configurator_circulation_count = fields.Integer(
        compute='_compute_configurator_circulation_count'
    )
    base_length = fields.Float(default=0)
    base_width = fields.Float(default=0)
    base_height = fields.Float(default=0)
    lid_height = fields.Float(default=0)
    lid_extra = fields.Float()
    lid_used = fields.Boolean(compute='_compute_lid_used')
    outside_wrapping_extra = fields.Float()
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
    print_house_id = fields.Many2one('package.print.house')
    component_length_width_editable = fields.Boolean(
        compute='_compute_package_type_options'
    )
    dimensions_visible = fields.Boolean(compute='_compute_package_type_options')

    @api.depends('configurator_insert_ids')
    def _compute_configurator_insert_count(self):
        for rec in self:
            rec.configurator_insert_count = len(rec.configurator_insert_ids)

    @api.depends('circulation_ids')
    def _compute_configurator_circulation_count(self):
        for rec in self:
            rec.configurator_circulation_count = len(rec.circulation_ids)

    @api.depends('package_type_id')
    def _compute_lid_used(self):
        for rec in self:
            codes = rec.package_type_id.component_type_ids.mapped('code')
            rec.lid_used = 'lid' in codes

    @api.depends(
        'base_length',
        'base_width',
        'base_height',
        'package_kind_id',
        'lid_height',
        'component_ids.sheet_id',
        'component_ids.fit_qty',
        'component_ids.component_type_id',
    )
    def _compute_description_warnings(self):
        for rec in self:
            rec.description_warnings = self.env[
                'package.warning'
            ].get_formatted_warnings(self)

    @api.depends('package_type_id')
    def _compute_package_type_options(self):
        for rec in self:
            # For now only editable for insert types.
            is_insert = rec.package_type_id.code == 'insert'
            rec.component_length_width_editable = is_insert
            rec.dimensions_visible = not is_insert

    @api.onchange('package_kind_id')
    def _onchange_box_type_id(self):
        if self.package_kind_id.default_component_ids and not self.component_ids:
            PackageComponent = self.env['package.configurator.component']
            for default_comp in self.package_kind_id.default_component_ids:
                self.component_ids |= PackageComponent.new(
                    {'component_type': default_comp.component_type}
                )

    @api.constrains(
        'package_kind_id',
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
            res = box.package_kind_id.validate_dimensions(
                box.base_length, box.base_width, box.base_height
            )
            box_type = box.package_kind_id
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

    def action_labor_processes(self):
        """Set labor and create/recreate its processes for each circulation item."""
        self.ensure_one()
        self.circulation_ids.create_circulation_labors()

    def action_open_cfg_inserts(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "package_configurator.package_configurator_insert_action"
        )
        domain = safe_eval(action['domain'])
        domain.append(('configurator_box_id', '=', self.id))
        action['domain'] = domain
        context = safe_eval(action['context'])
        context['default_configurator_box_id'] = self.id
        action['context'] = context
        return action

    def action_open_circulations(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "package_configurator.package_configurator_circulation_action"
        )
        action['domain'] = [('configurator_id', '=', self.id)]
        action['context'] = {'default_configurator_id': self.id}
        return action

    def _find_box_setups(self):
        self.ensure_one()
        domain = self._prepare_box_setups_domain()
        return self.env['package.setup'].search(domain)

    def _prepare_box_setups_domain(self):
        self.ensure_one()
        return [('company_id', '=', self.company_id.id)]
