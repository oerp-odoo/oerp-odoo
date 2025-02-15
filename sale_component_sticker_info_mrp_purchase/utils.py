from .const import STICKER_INFO_SEP


def get_sale_lines_from_stock_moves(moves):
    """Get sale lines from current stock moves or its first parent moves."""
    sale_lines = moves.mapped('sale_line_id')
    if sale_lines:
        return sale_lines
    group = moves.group_id
    parent_moves = group.mrp_production_ids.move_dest_ids
    if parent_moves:
        sale_lines = parent_moves.sale_line_id
        if sale_lines:
            return sale_lines
        return get_sale_lines_from_stock_moves(parent_moves)
    return moves.env['sale.order.line']


def get_sale_mos(mos):
    """Get first sale mos, either immediate or first parents that have it."""
    if not mos:
        return mos
    sale_mos = mos.filtered(lambda r: r.sale_order_count)
    if sale_mos:
        return sale_mos
    source_mos = mos.browse()
    for mo in mos:
        source_mos |= mo._get_sources()
    return get_sale_mos(source_mos)


def prepare_sale_group_name(sale_lines):
    group_names = sale_lines.filtered(lambda r: r.group_name).mapped('group_name')
    return ', '.join(gn for gn in group_names)


def prepare_component_sticker_info(mos, raw_product):
    infos = []
    for mo in mos:
        if mo.sale_group_name:
            infos.append(_prepare_component_sticker_info(mo, raw_product))
    return f'{STICKER_INFO_SEP} '.join(infos)


def _prepare_component_sticker_info(mo, raw_product):
    product = mo.product_id
    info = mo.sale_group_name
    if product.packaging_name:
        info = f'{info}, {product.packaging_name}'
    if mo.origin:
        info = f'{info}, {mo.origin}'
    qty = _gather_raw_product_quantity(mo, raw_product)
    if qty:
        info = f'{info} [QTY:{qty}]'
    return info


def _gather_raw_product_quantity(mo, raw_product):
    def filter_moves(product):
        return lambda r: r.product_id == product

    for descendant_mo in _get_descendant_mo(mo):
        # We gather quantity from first matched MO in a chain.
        moves = descendant_mo.move_raw_ids.filtered(filter_moves(raw_product))
        if not moves:
            continue
        return sum(m.product_uom_qty for m in moves)
    return 0.0


def _get_descendant_mo(mo):
    def get_child(mo):
        child_mos = mo._get_children()
        for child_mo in child_mos:
            yield child_mo
            yield from get_child(child_mo)

    yield mo
    yield from get_child(mo)
