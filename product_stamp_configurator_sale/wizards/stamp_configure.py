from odoo import api, fields, models

DESCRIPTION_MAP = {
    'die': 'description_sale',
    'counter_die': 'display_name',
    'mold': 'display_name',
}


class StampConfigure(models.TransientModel):
    """Extend to integrate with sale orders."""

    _inherit = 'stamp.configure'

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        ctx = self.env.context
        # Assuming single SO.
        if ctx.get('active_model') == 'sale.order' and ctx.get('active_ids'):
            sale = self.env['sale.order'].browse(ctx['active_ids'])
            res.update(self._get_sale_values(sale))
        return res

    sale_id = fields.Many2one('sale.order')

    @api.onchange('design_id')
    def _onchange_design_id(self):
        if self.design_id:
            self.sequence = self._get_sequence()

    @api.onchange('product_insert_die_ref_id')
    def _onchange_product_insert_die_ref_id(self):
        if self.product_insert_die_ref_id:
            # Find related SOL. Using only first found to simplify
            # logic..
            sol = self.env['sale.order.line'].search(
                [('product_id', '=', self.product_insert_die_ref_id.id)],
                limit=1,
            )
            if sol:
                self.quantity_dies = sol.product_uom_qty

    def prepare_product_insert_die_ref_domain(self):
        domain = super().prepare_product_insert_die_ref_domain()
        products = self.find_rel_document_products()
        # We include all products, but we expect base domain to filter
        # out that do not match products that can be insert die
        # reference.
        if products:
            domain.append(('id', 'in', products.ids))
        return domain

    def find_rel_document_products(self):
        """Find products on related document(s)."""
        self.ensure_one()
        return self.sale_id.order_line.mapped('product_id')

    def action_configure(self):
        res = super().action_configure()
        if self.sale_id:
            self._create_sale_lines(res)
        return res

    @api.model
    def _get_sale_values(self, sale):
        return {
            'partner_id': sale.partner_id.commercial_partner_id.id,
            'origin': sale.name,
            'ref': sale.client_order_ref,
            'sale_id': sale.id,
        }

    def _get_sequence(self):
        """Calculate sequence counting lines matching design category."""
        self.ensure_one()
        if not self.sale_id:
            return 1
        lines = self.sale_id.order_line
        category = self.design_id.category_id
        return 1 + sum(1 for line in lines if line.product_id.categ_id == category)

    def _create_sale_lines(self, cfg_results):
        self.ensure_one()
        line_datas = self._prepare_sale_lines(cfg_results)
        self.sale_id.write({'order_line': line_datas})
        return True

    def _prepare_sale_lines(self, cfg_results):
        self.ensure_one()
        line_datas = []
        for key, cfg_result in cfg_results.items():
            line_datas.append((0, 0, self._prepare_sale_line(key, cfg_result)))
        return line_datas

    def _prepare_sale_line(self, key, cfg_result):
        self.ensure_one()
        description_fname = DESCRIPTION_MAP[key]
        product = cfg_result['product']
        return {
            'product_id': product.id,
            'name': product[description_fname],
            'product_uom_qty': cfg_result['quantity'],
            'price_unit': cfg_result['price_unit'],
        }
