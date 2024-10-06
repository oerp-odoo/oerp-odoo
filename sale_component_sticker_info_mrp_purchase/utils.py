STICKER_INFO_SEP = ';'


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


def prepare_component_sticker_info(mos):
    infos = []
    for mo in mos:
        if mo.sale_group_name:
            infos.append(_prepare_component_sticker_info(mo))
    return f'{STICKER_INFO_SEP} '.join(infos)


def _prepare_component_sticker_info(mo):
    product = mo.product_id
    info = mo.sale_group_name
    if product.packaging_name:
        info = f'{info}, {product.packaging_name}'
    if mo.origin:
        info = f'{info}, {mo.origin}'
    return info
