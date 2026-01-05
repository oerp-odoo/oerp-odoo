# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale - Primary Sale Order",
    "version": "17.0.1.0.0",
    "summary": "Show primary sale order on inventory transfers",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Inventory",
    "depends": [
        # odoo
        "sale_stock",
        # oerp-odoo
        "procurement_group_parent_root",
    ],
    "data": ["views/stock_picking.xml"],
    'assets': {
        'web.assets_backend': ['sale_stock_primary_link/static/src/**/*.xml'],
    },
    "installable": True,
}
