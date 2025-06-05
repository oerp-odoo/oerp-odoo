# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Primary Sale Order Tags",
    "version": "17.0.1.0.0",
    "summary": "Show primary sale order tags on inventory transfers",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Inventory",
    "depends": [
        # oerp-odoo
        "sale_stock_primary_link",
    ],
    "data": ["views/stock_picking.xml"],
    "installable": True,
}
