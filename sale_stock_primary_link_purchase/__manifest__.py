# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale - Primary Sale Order on Purchase",
    "version": "17.0.1.0.0",
    "summary": "Show primary sale order on purchase orders",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Purchase",
    "depends": [
        # odoo
        "purchase_stock",
        # oerp-odoo
        "sale_stock_primary_link",
    ],
    "data": ["views/purchase_order.xml"],
    "installable": True,
}
