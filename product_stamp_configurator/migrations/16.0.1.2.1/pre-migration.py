from odoo.tools import column_exists, rename_column


def migrate(cr, version):
    table = 'stamp_material'
    old_name = 'weight_coefficient'
    new_name = 'weight'
    if column_exists(cr, table, old_name):
        rename_column(cr, table, old_name, new_name)
