from lxml import etree


def preprocess_arch_readonly_fields(
    arch, readonly_condition, ignored_fields=None, xpath='//field'
):
    if ignored_fields is None:
        ignored_fields = []
    archnode = etree.fromstring(arch)
    field_nodes = archnode.xpath(xpath)
    if not field_nodes:
        return arch
    for field_node in field_nodes:
        if field_node.get('name') in ignored_fields:
            continue
        orig_readonly = field_node.get('readonly')
        if orig_readonly:
            readonly = f'{orig_readonly} or {readonly_condition}'
        else:
            readonly = readonly_condition
        field_node.set('readonly', readonly)
    return etree.tostring(archnode, encoding='unicode')
