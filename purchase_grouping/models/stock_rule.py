from odoo import api, models


def get_domain_leaf_index(domain, left_part):
    for idx, leaf in enumerate(domain):
        if isinstance(leaf, tuple) and leaf[0] == left_part:
            return idx
    return -1


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        for (procurement, _rule) in procurements:
            procurement.values['product'] = procurement.product_id
        return super()._run_buy(procurements)

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        grouping = self.env.company.purchase_grouping
        if grouping == 'no_grouping':
            # To have a domain that will not find any match!
            domain += (('id', '=', 0),)
        elif grouping == 'root_procure_group' and values.get('group_id'):
            root_group_id = values['group_id'].parent_root_id.id
            # We must remove `group_id` domain, because it will be set
            # when group_propagation_option == 'propagate'. And here we
            # also expect that option, so group would actually be set on
            # purchase!
            leaf_idx = get_domain_leaf_index(domain, 'group_id')
            if leaf_idx != -1:
                domain_lst = list(domain)
                domain_lst.pop(leaf_idx)
                domain = tuple(domain_lst)
            domain += (('group_id.parent_root_id', '=', root_group_id),)
        product = values.get("product", self.env["product.product"])
        if grouping != 'no_grouping' and product.purchase_grouping_id:
            domain += (('purchase_grouping_id', '=', product.purchase_grouping_id.id),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        # values is actually a list of values and odoo uses the first one themselves..
        # So not sure why it even cares to send multiple.
        product = values[0].get('product')
        if not product:
            return res
        pg = product.purchase_grouping_id
        if not pg:
            return res
        res['purchase_grouping_id'] = pg.id
        return res
