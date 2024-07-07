def gather_group_names_with_sale_orders(products, sales):
    """Gather by matching products."""
    data = set()
    for product in products:
        for res in _gather_group_names_with_sale_orders(product, sales):
            data.add(res)
    return data


def prepare_sale_group_name(data: set[tuple], without_sale_name=False):
    if without_sale_name:
        return ', '.join(gn for (gn, __) in data)
    return ', '.join(f'{gn}, {so.name}' for (gn, so) in data)


def _gather_group_names_with_sale_orders(product, sales):
    for sale in sales:
        for line in sale.order_line:
            if line.group_name and line.product_id == product:
                yield (line.group_name, sale)
