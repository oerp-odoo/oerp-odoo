STICKER_INFO_SEP = ';'


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
