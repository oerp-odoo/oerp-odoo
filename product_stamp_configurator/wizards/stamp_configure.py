import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..const import DP_PRICE
from ..stamp import code, description, name, parsing, price
from ..utils import FieldTranslation, translate_field

# To filter nothing.
ALL_DOMAIN = [(1, '=', 1)]
# Common deps also include die deps, because nothing else can be computed
# before that.
PRICE_DEPS_COMMON = [
    'partner_id',
    'area_priced',
    'design_id',
    'material_id',
    'difficulty_id',
    'quantity_dies',
    'margin_ratio',
]
PRICE_DEPS_COUNTER_DIE = ['quantity_counter_dies']
PRICE_DEPS_MOLD = ['quantity_mold']
PRICE_SQCM_CUSTOM_FIELDS = [
    'price_sqcm_die_custom',
    'price_sqcm_counter_die_custom',
    'price_sqcm_mold_custom',
]
# Separated, because this is not mandatory to calculate it.
PRICE_EXTRA_DEPS = ['embossed_design_perc']
PRICE_COMPUTE_DEPS = (
    PRICE_DEPS_COMMON
    + PRICE_DEPS_COUNTER_DIE
    + PRICE_DEPS_MOLD
    + PRICE_EXTRA_DEPS
    + PRICE_SQCM_CUSTOM_FIELDS
)


def _get_default_prices_dict():
    return {
        'price_sqcm_die_suggested': 0.0,
        'price_sqcm_counter_die_suggested': 0.0,
        'price_sqcm_mold_suggested': 0.0,
        'price_unit_die': 0.0,
        'price_unit_counter_die': 0.0,
        'price_unit_mold': 0.0,
        'cost_unit_die': 0.0,
        'cost_unit_counter_die': 0.0,
        'cost_unit_mold': 0.0,
    }


class StampConfigure(models.TransientModel):
    """Model to configure stamp product using specific stamp logic."""

    _name = 'stamp.configure'
    _description = "Configure Stamp Product"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if res.get('company_id'):
            company = self.env['res.company'].browse(res['company_id'])
        else:
            company = self.env.company
        if 'die_id' in default_fields:
            res['die_id'] = company.die_default_id.id
        if 'category_counter_die_id' in default_fields:
            res['category_counter_die_id'] = company.category_default_counter_die_id.id
        if 'category_mold_id' in default_fields:
            res['category_mold_id'] = company.category_default_mold_id.id
        return res

    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
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
    flat_embossed_foiling = fields.Boolean(related='design_id.flat_embossed_foiling')
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
    area = fields.Float(compute='_compute_area')
    area_priced = fields.Float(compute='_compute_area')
    is_area_priced_greater = fields.Boolean(compute='_compute_area')
    origin = fields.Char("Quote No.")
    ref = fields.Char("Tool Reference")
    margin_ratio = fields.Float(
        digits=DP_PRICE,
        help="Multiplier that is used when calculating prices",
        default=1.0,
    )
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
    label_price_sqcm_suggested = fields.Char(compute='_compute_price_labels')
    label_price_sqcm_custom = fields.Char(compute='_compute_price_labels')
    label_price_unit = fields.Char(compute='_compute_price_labels')
    # Prices
    price_sqcm_die_suggested = fields.Float(
        "Suggested Die ㎠ Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    price_sqcm_counter_die_suggested = fields.Float(
        "Suggested Counter-Die ㎠ Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    price_sqcm_mold_suggested = fields.Float(
        "Suggested Mold ㎠ Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    price_sqcm_die_custom = fields.Float(
        "Custom Die ㎠ Price",
        digits=DP_PRICE,
    )
    price_sqcm_counter_die_custom = fields.Float(
        "Custom Counter-Die ㎠ Price", digits=DP_PRICE
    )
    price_sqcm_mold_custom = fields.Float("Custom Mold ㎠ Price", digits=DP_PRICE)
    price_unit_die = fields.Float(
        "Die Unit Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    price_unit_counter_die = fields.Float(
        "Counter-Die Unit Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    price_unit_mold = fields.Float(
        "Mold Unit Price",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    cost_unit_die = fields.Float(
        "Die Unit Cost",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    cost_unit_counter_die = fields.Float(
        "Counter-Die Unit Cost",
        digits=DP_PRICE,
        compute='_compute_prices',
    )
    cost_unit_mold = fields.Float(
        "Mold Unit Cost",
        digits=DP_PRICE,
        compute='_compute_prices',
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

    @api.depends('size_length', 'size_width', 'partner_id.property_stamp_pricelist_id')
    def _compute_area(self):
        for rec in self:
            area = rec.size_length * rec.size_width
            rec.area = area
            min_area = rec.partner_id.property_stamp_pricelist_id.min_area
            # We should use priced area 0 if area is zero (not entered)
            # to not use minimum area when we don't know entered area.
            area_priced = area and max(area, min_area) or 0.0
            rec.area_priced = area_priced
            rec.is_area_priced_greater = area_priced > area

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

    @api.depends('company_id.currency_id.name')
    def _compute_price_labels(self):
        for cfg in self:
            currency_name = cfg.company_id.currency_id.name
            cfg.update(
                {
                    'label_price_sqcm_suggested': _("%s/㎠ Pricelist", currency_name),
                    'label_price_sqcm_custom': _("%s/㎠ Revised", currency_name),
                    'label_price_unit': _("%s/pcs", currency_name),
                }
            )

    @api.depends(*PRICE_COMPUTE_DEPS)
    def _compute_prices(self):
        digits = self.env['decimal.precision'].precision_get(DP_PRICE)
        for cfg in self:
            mr = cfg.margin_ratio
            prices = _get_default_prices_dict()
            # All common deps must be set, to compute price for anything.
            if all(cfg[fname] for fname in PRICE_DEPS_COMMON):
                price_unit_die_suggested = price.calc_die_price(self, digits=digits)
                (
                    price_sqcm_die_suggested,
                    price_unit_die,
                ) = price.calc_price_sqcm_suggested_and_price_unit(
                    self,
                    price_unit_die_suggested,
                    # Custom price is entered as is, but final price
                    # must take margin ratio into consideration.
                    price_sqcm_custom=mr * self.price_sqcm_die_custom,
                    digits=digits,
                )
                cost_unit_die = price.calc_price_sqcm_suggested_and_price_unit(
                    self,
                    price.calc_die_price(self, digits=digits, with_margin=False),
                    price_sqcm_custom=self.price_sqcm_die_custom,
                    digits=digits,
                )[1]
                prices.update(
                    {
                        'price_sqcm_die_suggested': price_sqcm_die_suggested,
                        'price_unit_die': price_unit_die,
                        'cost_unit_die': cost_unit_die,
                    }
                )
                if all(cfg[fname] for fname in PRICE_DEPS_COUNTER_DIE):
                    price_unit_counter_die_suggested = price.calc_counter_die_price(
                        self, digits=digits
                    )
                    (
                        price_sqcm_counter_die_suggested,
                        price_unit_counter_die,
                    ) = price.calc_price_sqcm_suggested_and_price_unit(
                        self,
                        price_unit_counter_die_suggested,
                        price_sqcm_custom=mr * self.price_sqcm_counter_die_custom,
                        digits=digits,
                    )
                    (
                        cost_unit_counter_die
                    ) = price.calc_price_sqcm_suggested_and_price_unit(
                        self,
                        price.calc_counter_die_price(
                            self, digits=digits, with_margin=False
                        ),
                        price_sqcm_custom=self.price_sqcm_counter_die_custom,
                        digits=digits,
                    )[
                        1
                    ]
                    prices.update(
                        {
                            'price_sqcm_counter_die_suggested': (
                                price_sqcm_counter_die_suggested
                            ),
                            'price_unit_counter_die': price_unit_counter_die,
                            'cost_unit_counter_die': cost_unit_counter_die,
                        }
                    )
                if all(cfg[fname] for fname in PRICE_DEPS_MOLD):
                    price_unit_mold_suggested = price.calc_mold_price(
                        self, digits=digits
                    )
                    (
                        price_sqcm_mold_suggested,
                        price_unit_mold,
                    ) = price.calc_price_sqcm_suggested_and_price_unit(
                        self,
                        price_unit_mold_suggested,
                        price_sqcm_custom=mr * self.price_sqcm_mold_custom,
                        digits=digits,
                    )
                    cost_unit_mold = price.calc_price_sqcm_suggested_and_price_unit(
                        self,
                        price.calc_mold_price(self, digits=digits, with_margin=False),
                        price_sqcm_custom=self.price_sqcm_mold_custom,
                        digits=digits,
                    )[1]
                    prices.update(
                        {
                            'price_sqcm_mold_suggested': price_sqcm_mold_suggested,
                            'price_unit_mold': price_unit_mold,
                            'cost_unit_mold': cost_unit_mold,
                        }
                    )
            self.update(prices)

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

    @api.constrains(
        'price_sqcm_counter_die_custom',
        'price_sqcm_counter_die_custom',
        'price_sqcm_mold_custom',
    )
    def _check_custom_prices(self):
        for rec in self:
            if any(rec[fname] < 0 for fname in PRICE_SQCM_CUSTOM_FIELDS):
                raise ValidationError(_("Custom ㎠ Price must be 0 or greater!"))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        pricelist = self.partner_id.property_stamp_pricelist_id
        if pricelist:
            self.margin_ratio = pricelist.margin_default_ratio

    @api.onchange('die_id')
    def _onchange_die_id(self):
        domain = ALL_DOMAIN
        if self.is_insert_die:
            domain = self.prepare_product_insert_die_ref_domain()
        else:
            self.update(
                {
                    'product_insert_die_ref_id': False,
                    'insert_die_ref': False,
                }
            )
        # TODO: redesign this as returning domain from onchange is deprecated.
        return {'domain': {'product_insert_die_ref_id': domain}}

    @api.onchange('quantity_dies')
    def _onchange_quantity_dies(self):
        if self.is_embossed:
            # TODO: should we update quantity_counter_dies even if it is
            # already non zero quantity?..
            self.quantity_counter_dies = self.quantity_dies

    @api.onchange('quantity_counter_dies')
    def _onchange_quantity_counter_dies(self):
        if not self.quantity_counter_dies:
            self.update(
                {
                    'quantity_counter_spare_dies': 0,
                    'material_counter_id': False,
                }
            )

    # TODO: what the hell, why naming method `_onchange_design_id` makes
    # onchange to never trigger?..
    @api.onchange('design_id')
    def _onchange_design(self):
        quantity_mold = 0
        if self.design_id.is_embossed:
            quantity_mold = self.env.company.quantity_mold_default
        self.update(
            {
                'embossed_design_perc': 0,
                'quantity_counter_dies': 0,
                'quantity_mold': quantity_mold,
            }
        )

    def prepare_product_insert_die_ref_domain(self):
        self.ensure_one()
        return [('stamp_type', '=', 'die'), ('is_insert_die', '=', False)]

    def action_configure(self):
        """Create products with details using stamp configurator."""
        self.ensure_one()
        self._validate_categories()
        res = {'die': self._create_die()}
        msg_data = self._prepare_message()
        self._post_product_configurator_message(res['die']['product'], msg_data)
        if self.quantity_counter_dies_total > 0:
            res['counter_die'] = self._create_counter_die()
            self._post_product_configurator_message(
                res['counter_die']['product'], msg_data
            )
        if self.quantity_mold > 0:
            res['mold'] = self._create_mold()
            self._post_product_configurator_message(res['mold']['product'], msg_data)
        self._translate_products(res)
        return res

    def _validate_categories(self):
        self.ensure_one()
        self.design_id.category_id.validate_stamp_type('die')
        self.category_counter_die_id.validate_stamp_type('counter_die')
        self.category_mold_id.validate_stamp_type('mold')

    def _prepare_common_product_vals(self, stamp_type):
        self.ensure_one()
        company = self.company_id
        return {'company_id': False if company.stamp_products_shared else company.id}

    def _prepare_common_product_die_vals(self):
        """Return common vals for die and counter die products."""
        self.ensure_one()
        return {
            # TODO: for now we have fixed type, but might be good to
            # be able to specify one via design?
            'detailed_type': 'consu',
        }

    def _calc_weight(self, material):
        self.ensure_one()
        return self.area * self.design_id.weight_coefficient * material.weight

    def _create_die(self):
        self.ensure_one()
        return {
            'product': self._create_die_product(),
            'price_unit': self.price_unit_die,
            'quantity': self.quantity_dies_total,
        }

    def _create_counter_die(self):
        self.ensure_one()
        return {
            'product': self._create_counter_die_product(),
            'price_unit': self.price_unit_counter_die,
            'quantity': self.quantity_counter_dies_total,
        }

    def _create_mold(self):
        self.ensure_one()
        return {
            'product': self._create_mold_product(),
            'price_unit': self.price_unit_mold,
            'quantity': self.quantity_mold,
        }

    def _create_die_product(self):
        self.ensure_one()
        return self.env['product.product'].create(self._prepare_die_product())

    def _create_counter_die_product(self):
        self.ensure_one()
        return self.env['product.product'].create(self._prepare_counter_die_product())

    def _create_mold_product(self):
        self.ensure_one()
        return self.env['product.product'].create(self._prepare_mold_product())

    def _prepare_die_product(self):
        self.ensure_one()
        price_unit = self.price_unit_die
        return {
            **self._prepare_common_product_vals('die'),
            'is_insert_die': self.is_insert_die,
            'weight': self._calc_weight(self.material_id),
            'categ_id': self.design_id.category_id.id,
            'default_code': code.generate_die_code(self),
            'name': name.generate_die_name(self),
            # TODO: should we propagate price_digits/engraving_digits
            # from here? Currently we use default ones when generating
            # description.
            'description_sale': description.generate_die_description(self, price_unit),
            'list_price': price_unit,
            **self._prepare_common_product_die_vals(),
        }

    def _prepare_counter_die_product(self):
        self.ensure_one()
        return {
            **self._prepare_common_product_vals('counter_die'),
            'weight': self._calc_weight(self.material_counter_id),
            'categ_id': self.category_counter_die_id.id,
            'default_code': code.generate_counter_die_code(self),
            'name': name.generate_counter_die_name(self),
            'list_price': self.price_unit_counter_die,
            **self._prepare_common_product_die_vals(),
        }

    def _prepare_mold_product(self):
        self.ensure_one()
        return {
            **self._prepare_common_product_vals('mold'),
            'weight': self._calc_weight(self.material_id),
            'categ_id': self.category_mold_id.id,
            'detailed_type': 'service',
            'default_code': code.generate_mold_code(self),
            'name': name.generate_mold_name(self),
            'list_price': self.price_unit_mold,
        }

    def _prepare_message(self):
        self.ensure_one()
        data = {
            'sequence': self.sequence,
            'sequence_counter_die': self.sequence_counter_die,
            'partner_name': self.partner_id.name,
            'die_code': self.die_id.code,
            'is_insert_die': self.is_insert_die,
            'design_code': self.design_id.code,
            'material_code': self.material_id.code,
            'material_counter_code': self.material_counter_id.code,
            'finishing_code': self.finishing_id.code,
            'difficulty': self.difficulty_id.name,
            'size_length': self.size_length,
            'size_width': self.size_width,
            'origin': self.origin,
            'ref': self.ref,
            'quantity_dies': self.quantity_dies,
            'quantity_spare_dies': self.quantity_spare_dies,
            'quantity_counter_dies': self.quantity_counter_dies,
            'quantity_counter_spare_dies': self.quantity_counter_spare_dies,
            'quantity_mold': self.quantity_mold,
            'category_counter_die_name': self.category_counter_die_id.name,
            'category_mold_name': self.category_mold_id.name,
        }
        if self.product_insert_die_ref_id:
            data[
                'product_insert_die_ref_code'
            ] = self.product_insert_die_ref_id.default_code
        if self.flat_embossed_foiling:
            data['embossed_design_perc'] = self.embossed_design_perc
        return data

    def _post_product_configurator_message(self, product, data):
        self.ensure_one()
        data_str = json.dumps(data, indent=2)
        body = (
            '<strong>Stamp Configurator Parameters Used:</strong>'
            f'<pre>\n\n{data_str}</pre>'
        )
        # Post on both product.product and product.template for convenience..
        product.message_post(body=body)
        product.product_tmpl_id.message_post(body=body)
        return True

    def _translate_products(self, data):
        def translate_product_name(product, func):
            field_translation = FieldTranslation(
                fname='name',
                record=product,
                langs=lang_codes,
                func=func,
                first_func_arg=self,
            )
            translate_field(field_translation)

        # die will always be created, so we always expect it.
        langs = self.env['res.lang'].search([('active', '=', True)])
        lang_codes = tuple(langs.mapped('code'))
        die_product = data['die']['product']
        translate_product_name(die_product, name.generate_die_name)
        if data.get('counter_die'):
            translate_product_name(
                data['counter_die']['product'], name.generate_counter_die_name
            )
        if data.get('mold'):
            translate_product_name(data['mold']['product'], name.generate_mold_name)
