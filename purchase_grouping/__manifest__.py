# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Purchase - Grouping",
    "version": "17.0.1.0.0",
    "summary": "Extra ways to group purchase orders",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Purchase",
    "depends": [
        # odoo
        "purchase_stock",
        # oerp-odoo
        "procurement_group_parent_root",
    ],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/purchase_grouping.xml",
        "views/product_template.xml",
        "views/purchase_order.xml",
    ],
}
