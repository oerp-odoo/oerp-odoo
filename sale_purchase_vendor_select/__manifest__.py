# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale Purchase - Select Vendor",
    "version": "17.0.1.0.0",
    "summary": "Select Vendor for purchases before confirming Sale Order",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Sales/Sales",
    "depends": [
        # odoo
        "sale_stock",
        "purchase_stock",
        "sale_purchase",
    ],
    "data": ["views/sale_order.xml"],
    "installable": False,
}
