def prepare_mts_else_mto_max_qty_perc_data(procurements_w_rules):
    data = {}
    for procurement, rule in procurements_w_rules:
        product = procurement.product_id
        if not is_mto_by_orderpoint_max_qty_perc(product, rule):
            continue
        location = rule.location_src_id
        orderpoint = _get_orderpoint(product, location)
        if not orderpoint:
            continue
        data.setdefault((location.id, product.id), [])
        perc = rule.route_id.orderpoint_max_qty_perc
        qty_threshold = perc * orderpoint.product_max_qty / 100
        # We append so data could be consumed by context if there would be
        # multiple products with same location.
        data[(location.id, product.id)].append(qty_threshold)
    return data


def is_mto_by_orderpoint_max_qty_perc(product, rule):
    return (
        _is_rule_mts_else_mto(rule)
        and rule.route_id.mts_else_mto_condition == 'orderpoint_max_qty_perc'
        and _is_product_mts_else_mto(product, rule)
    )


def _is_rule_mts_else_mto(rule):
    return rule.procure_method == 'mts_else_mto' and rule.action in ('pull', 'push')


def _is_product_mts_else_mto(product, rule):
    if not product.orderpoint_ids:
        return False
    # NOTE. For now, such route must be explicitly set on product!
    return rule.route_id in product.route_ids


def _get_orderpoint(product, location):
    return product.orderpoint_ids.filtered(lambda r: r.location_id == location)
