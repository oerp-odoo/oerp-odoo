from odoo.tools import column_exists, rename_column


def migrate(cr, version):
    table = 'stamp_design'
    old_name = 'is_embossed'
    new_name = 'flat_embossed_foiling'
    if column_exists(cr, table, old_name):
        rename_column(cr, table, old_name, new_name)
