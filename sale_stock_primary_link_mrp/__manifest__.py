# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale - Primary Sale Order on Manufacturing",
    "version": "17.0.1.0.0",
    "summary": "Show primary sale order on manufacturing orders",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Manufacturing",
    "depends": [
        # odoo
        "mrp",
        # oerp-odoo
        "sale_stock_primary_link",
    ],
    "data": ["views/mrp_production.xml"],
    "installable": True,
}
