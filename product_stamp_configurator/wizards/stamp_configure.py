from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..stamp import code, description, name, parsing, price

# To filter nothing.
ALL_DOMAIN = [(1, '=', 1)]


class StampConfigure(models.TransientModel):
    """Model to configure stamp product using specific stamp logic."""

    _name = 'stamp.configure'
    _description = "Configure Stamp Product"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        company = self.env.company
        if 'category_counter_die_id' in default_fields:
            res['category_counter_die_id'] = company.category_default_counter_die_id.id
        if 'category_mold_id' in default_fields:
            res['category_mold_id'] = company.category_default_mold_id.id
        if 'quantity_mold' in default_fields:
            res['quantity_mold'] = company.quantity_mold_default
        return res

    sequence = fields.Integer(required=True, default=1)
    sequence_counter_die = fields.Integer(default=1)
    partner_id = fields.Many2one('res.partner', required=True, string="Customer")
    die_id = fields.Many2one('stamp.die', string="Die Type", required=True)
    product_insert_die_ref_id = fields.Many2one(
        'product.product', string="Reference to Master Die (Product)"
    )
    insert_die_ref = fields.Char(
        string="Reference to Master Die",
        compute='_compute_insert_die_ref',
        readonly=False,
        store=True,
    )
    is_insert_die = fields.Boolean(compute='_compute_is_insert_die')
    design_id = fields.Many2one('stamp.design', string="Design Type", required=True)
    is_embossed = fields.Boolean(related='design_id.is_embossed')
    embossed_design_perc = fields.Float("% of embossed design")
    material_id = fields.Many2one('stamp.material', required=True)
    material_counter_id = fields.Many2one('stamp.material', "Counter-Die Material")
    finishing_id = fields.Many2one('stamp.finishing', string="Special Finishing")
    difficulty_id = fields.Many2one(
        'stamp.difficulty', string="Difficulty Level", required=True
    )
    size_length = fields.Float("Size (length), cm", required=True)
    size_width = fields.Float("Size (width), cm", required=True)
    area = fields.Float(compute="_compute_area")
    origin = fields.Char("Quote No.")
    ref = fields.Char("Customer Reference")
    quantity_dies = fields.Integer("Quantity of Dies")
    quantity_spare_dies = fields.Integer("Spare Quantity of Dies")
    quantity_dies_total = fields.Integer(
        "Total Quantity of Dies", compute='_compute_quantity_dies_total'
    )
    quantity_counter_dies = fields.Integer("Quantity of Counter-Dies")
    quantity_counter_spare_dies = fields.Integer("Spare Quantity of Counter-Dies")
    quantity_counter_dies_total = fields.Integer(
        "Total Quantity of Counter Dies", compute='_compute_quantity_counter_dies_total'
    )
    quantity_mold = fields.Integer("Mold Quantity")
    category_counter_die_id = fields.Many2one(
        'product.category',
        'Counter-Die Category',
        domain=[('stamp_type', '=', 'counter_die')],
    )
    category_mold_id = fields.Many2one(
        'product.category', 'Mold Category', domain=[('stamp_type', '=', 'mold')]
    )

    @api.depends('product_insert_die_ref_id.default_code')
    @api.depends_context('company')
    def _compute_insert_die_ref(self):
        for rec in self:
            ref = False
            code = rec.product_insert_die_ref_id.default_code
            if code:
                design_codes = self.env['stamp.design'].get_design_codes(
                    company_id=self.env.company.id
                )
                ref = (
                    parsing.parse_design_seq_code(code, design_codes=design_codes)
                    or False
                )
            rec.insert_die_ref = ref

    @api.depends('die_id.code')
    def _compute_is_insert_die(self):
        for rec in self:
            rec.is_insert_die = parsing.is_insert_die_code(rec.die_id.code or '')

    @api.depends('size_length', 'size_width')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.size_length * rec.size_width

    @api.depends('quantity_dies', 'quantity_spare_dies')
    def _compute_quantity_dies_total(self):
        for rec in self:
            rec.quantity_dies_total = rec.quantity_dies + rec.quantity_spare_dies

    @api.depends('quantity_counter_dies', 'quantity_counter_spare_dies')
    def _compute_quantity_counter_dies_total(self):
        for rec in self:
            rec.quantity_counter_dies_total = (
                rec.quantity_counter_dies + rec.quantity_counter_spare_dies
            )

    @api.constrains('sequence')
    def _check_sequence(self):
        for rec in self:
            if rec.sequence <= 0:
                raise ValidationError(_("Sequence must be greater than 0"))

    @api.constrains('size_length', 'size_width')
    def _check_dimensions(self):
        for rec in self:
            if rec.size_length <= 0 or rec.size_width <= 0:
                raise ValidationError(
                    _(
                        "'Size (length), cm' and 'Size (width), cm', "
                        + "must be greater than 0"
                    )
                )

    @api.constrains('quantity_dies', 'quantity_spare_dies')
    def _check_quantity_dies(self):
        for rec in self:
            if not rec.quantity_dies_total:
                raise ValidationError(
                    _("Total Quantity of Dies must be greater than 0")
                )
            if rec.quantity_dies < 0:
                raise ValidationError(_("Quantity of Dies must not be negative"))
            if rec.quantity_spare_dies < 0:
                raise ValidationError(_("Spare Quantity of Dies must not be negative"))

    @api.constrains('quantity_counter_dies', 'quantity_counter_spare_dies')
    def _check_quantity_counter_dies(self):
        for rec in self:
            if rec.quantity_counter_dies < 0:
                raise ValidationError(
                    _("Quantity of Counter-Dies must not be negative")
                )
            if rec.quantity_counter_spare_dies < 0:
                raise ValidationError(
                    _("Spare Quantity of Counter-Dies must not be negative")
                )

    @api.constrains('quantity_mold')
    def _check_quantity_mold(self):
        for rec in self:
            if rec.quantity_mold < 0:
                raise ValidationError(_("Mold Quantity must not be negative"))

    @api.onchange('die_id')
    def _onchange_die_id(self):
        domain = ALL_DOMAIN
        if self.is_insert_die:
            domain = self.prepare_product_insert_die_ref_domain()
        else:
            self.product_insert_die_ref_id = False
        return {'domain': {'product_insert_die_ref_id': domain}}

    def prepare_product_insert_die_ref_domain(self):
        self.ensure_one()
        return [('stamp_type', '=', 'die'), ('is_insert_die', '=', False)]

    def action_configure(self):
        """Create products with details using stamp configurator."""
        self.ensure_one()
        self._validate_categories()
        res = {'die': self._create_die()}
        if self.quantity_counter_dies_total > 0:
            res['counter_die'] = self._create_counter_die()
        if self.quantity_mold > 0:
            res['mold'] = self._create_mold()
        return res

    def _validate_categories(self):
        self.ensure_one()
        self.design_id.category_id.validate_stamp_type('die')
        self.category_counter_die_id.validate_stamp_type('counter_die')
        self.category_mold_id.validate_stamp_type('mold')

    def _prepare_common_product_vals(self):
        self.ensure_one()
        return {
            'company_id': self.env.company.id,
        }

    def _calc_weight(self, material):
        self.ensure_one()
        return (
            self.area * self.design_id.weight_coefficient * material.weight_coefficient
        )

    def _create_die(self):
        self.ensure_one()
        price_unit = price.calc_die_price(self)
        return {
            'product': self._create_die_product(price_unit),
            'price_unit': price_unit,
            'quantity': self.quantity_dies_total,
        }

    def _create_counter_die(self):
        self.ensure_one()
        price_unit = price.calc_counter_die_price(self)
        return {
            'product': self._create_counter_die_product(price_unit),
            'price_unit': price_unit,
            'quantity': self.quantity_counter_dies_total,
        }

    def _create_mold(self):
        self.ensure_one()
        price_unit = price.calc_mold_price(self)
        return {
            'product': self._create_mold_product(price_unit),
            'price_unit': price_unit,
            'quantity': self.quantity_mold,
        }

    def _create_die_product(self, price_unit):
        self.ensure_one()
        return self.env['product.product'].create(
            {
                **self._prepare_common_product_vals(),
                'is_insert_die': self.is_insert_die,
                'weight': self._calc_weight(self.design_id),
                'categ_id': self.design_id.category_id.id,
                # TODO: for now we have fixed type, but might be good to
                # be able to specify one via design?
                'detailed_type': 'consu',
                'default_code': code.generate_die_code(self),
                'name': name.generate_die_name(self),
                'description_sale': description.generate_die_description(
                    self, price_unit
                ),
                'list_price': price_unit,
            }
        )

    def _create_counter_die_product(self, price_unit):
        self.ensure_one()
        return self.env['product.product'].create(
            {
                **self._prepare_common_product_vals(),
                'weight': self._calc_weight(self.material_counter_id),
                'categ_id': self.category_counter_die_id.id,
                'detailed_type': 'consu',
                'default_code': code.generate_counter_die_code(self),
                'name': name.generate_counter_die_name(self),
                'list_price': price_unit,
            }
        )

    def _create_mold_product(self, price_unit):
        self.ensure_one()
        return self.env['product.product'].create(
            {
                **self._prepare_common_product_vals(),
                'weight': self._calc_weight(self.design_id),
                'categ_id': self.category_mold_id.id,
                'detailed_type': 'service',
                'default_code': code.generate_mold_code(self),
                'name': name.generate_mold_name(self),
                'list_price': price_unit,
            }
        )
