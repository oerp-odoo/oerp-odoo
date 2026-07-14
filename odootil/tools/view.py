from lxml import etree

from odoo.models import BaseModel


def preprocess_arch_readonly_fields(
    model: BaseModel, arch, readonly_condition, ignored_fields=None, xpath='//field'
):
    if ignored_fields is None:
        ignored_fields = []
    archnode = etree.fromstring(arch)
    field_nodes = archnode.xpath(xpath)
    if not field_nodes:
        return arch
    for field_node in field_nodes:
        if _is_readonly_ignored_field(model, field_node, ignored_fields):
            continue
        orig_readonly = field_node.get('readonly')
        if orig_readonly:
            readonly = f'{orig_readonly} or {readonly_condition}'
        else:
            readonly = readonly_condition
        field_node.set('readonly', readonly)
    return etree.tostring(archnode, encoding='unicode')


def _is_readonly_ignored_field(model: BaseModel, field_node, ignored_fields: list[str]):
    fname = field_node.get('name')
    if fname in ignored_fields:
        return True
    # If view has readonly condition, it means python's readonly is
    # already overwritten.
    if field_node.get('readonly'):
        return False
    field = model._fields.get(fname)
    # We ignore if its made readonly in python as we would be overwriting
    # it with conditional readonly then.
    return field.readonly
