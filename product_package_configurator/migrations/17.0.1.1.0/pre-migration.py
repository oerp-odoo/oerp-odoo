from odoo.tools import column_exists, rename_column


def migrate(cr, version):
    table = 'package_configurator_box'
    old_name = 'carton_id'
    new_name = 'carton_base_id'
    if column_exists(cr, table, old_name):
        rename_column(cr, table, old_name, new_name)
