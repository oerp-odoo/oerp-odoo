from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import utils
from ..value_objects import layout as vo_layout


class PackageConfiguratorComponent(models.Model):
    _name = 'package.configurator.component'
    _description = "Package Configurator Component"
    _rec_name = 'component_type_id'

    configurator_id = fields.Many2one(
        'package.configurator', required=True, ondelete='cascade'
    )
    component_type_allowed_ids = fields.Many2many(
        related='configurator_id.package_type_id.component_type_ids'
    )
    component_type_id = fields.Many2one(
        'package.component.type',
        required=True,
        domain="[('id', 'in', component_type_allowed_ids)]",
    )
    # TODO: make sure these private fields won't appear in search in UI!
    _component_length = fields.Float(string="Length (Custom)")
    _component_width = fields.Float(string="Width (Custom)")
    component_length = fields.Float(
        compute='_compute_type_data',
        # inverse='_inverse_component_length',
        string="Length",
    )
    component_width = fields.Float(
        compute='_compute_type_data',
        # inverse='_inverse_component_width',
        string="Width",
    )
    component_kind_ids = fields.Many2many(
        related='component_type_id.component_kind_ids'
    )
    component_kind_allowed_ids = fields.Many2many(
        'package.component.kind',
        compute='_compute_component_kind_allowed_ids',
        help="Component Kinds that can be used with this Component",
    )
    wrappingpaper_used = fields.Boolean(compute='_compute_component_kind_allowed_ids')
    sheet_type_id = fields.Many2one(
        'package.sheet.type',
        domain="[('component_kind_id', 'in', component_kind_allowed_ids)]",
    )
    sheet_id = fields.Many2one(
        'package.sheet',
        required=True,
        domain="[('component_kind_id', 'in', component_kind_allowed_ids)]",
        store=True,
        readonly=False,
        compute='_compute_sheet_id',
    )
    print_color_id = fields.Many2one('package.print.color')
    sheet_usable_length = fields.Float(compute='_compute_type_data')
    sheet_usable_width = fields.Float(compute='_compute_type_data')
    fit_qty = fields.Integer(
        compute='_compute_type_data',
        string="Fit Quantity",
        help="How many box layouts would fit on single raw sheet",
    )

    @api.depends(
        'component_type_id',
        'sheet_id',
        'print_color_id',
        '_component_length',
        '_component_width',
        'configurator_id.base_length',
        'configurator_id.base_width',
        'configurator_id.lid_height',
        'configurator_id.lid_extra',
        'configurator_id.outside_wrapping_extra',
        'configurator_id.component_ids.component_type_id',
        'configurator_id.print_house_id',
    )
    def _compute_type_data(self):
        for rec in self:
            data = rec._get_init_type_data()
            rec.update(data)
        configs = self.mapped('configurator_id')
        for cfg in configs:
            res = self.env['package.box.layout'].get_cfg_layouts(cfg)
            for ctype, layout in res.items():
                for comp in cfg.component_ids:
                    if comp.component_type_id.code != ctype:
                        continue
                    comp.update(
                        {
                            # TODO: move length/width to separate compute. Now
                            # with/length is filled only if sheet is selected. But it
                            # should only be needed for fit_qty, not component_length
                            # and component_width!
                            **comp._calc_length_width(layout),
                            **comp._get_sheet_usable_dimensions_data(),
                        }
                    )
                    # NOTE. We must wait, before component_length, component_width
                    # is set as it is needed for _calc_fit_qty
                    comp.fit_qty = comp._calc_fit_qty()
                    break

    @api.depends('component_type_id', 'configurator_id.package_type_id')
    def _compute_component_kind_allowed_ids(self):
        for rec in self:
            kinds = (
                rec.component_type_id.component_kind_ids
                & rec.configurator_id.package_type_id.component_kind_ids
            )
            rec.component_kind_allowed_ids = kinds
            rec.wrappingpaper_used = 'wrappingpaper' in kinds.mapped('code')

    @api.depends('sheet_type_id')
    def _compute_sheet_id(self):
        for rec in self:
            if not rec.sheet_type_id:
                continue
            # We can't rely on component_length, component_width compute,
            # because this one can be computed earlier and then those
            # values would be 0, so we directly get result from get_cfg_layouts!
            layout = self.env['package.box.layout'].get_cfg_layouts(
                rec.configurator_id
            )[rec.component_type_id.code]
            res = rec._calc_length_width(layout)
            length = res['component_length']
            width = res['component_width']
            if not length or not width:
                continue
            rec.sheet_id = rec.env['package.sheet.match'].match(
                rec.sheet_type_id,
                vo_layout.Layout2D(length=length, width=width),
            )

    @api.onchange('component_type_id')
    def _onchange_component_type_id(self):
        if not self.component_type_id:
            return
        if self.sheet_type_id:
            self.sheet_type_id = False
        if self.sheet_id:
            self.sheet_id = False

    @api.constrains('component_type_id')
    def _check_component_type_id(self):
        configs = self.mapped('configurator_id')
        for cfg in configs:
            ctypes = [c.component_type_id.code for c in cfg.component_ids]
            if 'base' not in ctypes:
                raise ValidationError(_("Base component is required!"))
            if len(ctypes) != len(set(ctypes)):
                raise ValidationError(
                    _("Component types must be unique per configurator!")
                )

    @api.constrains('component_type_id', 'sheet_type_id', 'sheet_id')
    def _check_component_kind_ids(self):
        for rec in self:
            msg = _(
                "Kind mismatch. It must match between component options! And be in "
                + "allowed list per component/package type!"
            )
            if rec.sheet_id.component_kind_id not in rec.component_kind_allowed_ids:
                raise ValidationError(msg)
            if (
                rec.sheet_type_id
                and rec.sheet_type_id.component_kind_id
                not in rec.component_kind_allowed_ids
            ):
                raise ValidationError(msg)

    def _calc_length_width(self, layout: vo_layout.Layout2D):
        def calc(custom_dim, layout_dimension):
            if custom_dim:
                return custom_dim + (
                    # Even if custom value was entered, it must add global extra!
                    self.configurator_id.company_id.package_default_global_box_extra
                )
            return layout_dimension

        self.ensure_one()
        return {
            'component_length': calc(self._component_length, layout.length),
            'component_width': calc(self._component_width, layout.width),
        }

    def _get_sheet_usable_dimensions_data(self):
        self.ensure_one()
        sheet = self.sheet_id
        # Print house limitations can only be used if component uses
        # color. Otherwise it means, no printing will be used for this
        # component!
        house = self.configurator_id.print_house_id
        if not self.print_color_id:
            # Force empty recordset.
            house = house.browse()
        return {
            'sheet_usable_length': min(
                # If max is not set, it means, we have no limit, so we use sheet
                # length!
                sheet.sheet_length,
                house.print_max_length or sheet.sheet_length,
            ),
            'sheet_usable_width': min(
                sheet.sheet_width, house.print_max_width or sheet.sheet_width
            ),
        }

    def _calc_fit_qty(self):
        def can_calc():
            return (
                self.component_length
                and self.component_width
                and self.sheet_usable_length
                and self.sheet_usable_width
            )

        self.ensure_one()
        if not can_calc():
            return 0
        product_layout = vo_layout.Layout2D(
            length=self.component_length, width=self.component_width
        )
        sheet_layout = vo_layout.Layout2D(
            length=self.sheet_usable_length, width=self.sheet_usable_width
        )
        layout_fitter = vo_layout.LayoutFitter(
            product_layout=product_layout, sheet_layout=sheet_layout
        )
        return utils.fitter.calc_fit_quantity(layout_fitter)

    def _get_init_type_data(self):
        self.ensure_one()
        return {
            'fit_qty': 0,
            'component_length': 0.0,
            'component_width': 0.0,
            'sheet_usable_length': 0.0,
            'sheet_usable_width': 0.0,
        }
