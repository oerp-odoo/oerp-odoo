from odoo import models


def get_domain_leaf_index(domain, left_part):
    for idx, leaf in enumerate(domain):
        if isinstance(leaf, tuple) and leaf[0] == left_part:
            return idx
    return -1


class StockRule(models.Model):
    _inherit = 'stock.rule'

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
        return domain
